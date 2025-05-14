# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from ast import literal_eval

import decorator

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import groupby


@decorator.decorator
def check_approval_rules(func, action_type="confirm", *args, **kwargs):
    self = args[0]
    active_requests = False
    app_requests = self.env["approval.request"]
    # We are grouping all records by company for which an action is being called
    # to check if approval request needs to be generated.
    model_name = self._name
    for company, company_grouped_records in groupby(self, lambda x: x.company_id):

        # First we need to find the matched rules from which we are going to
        # select the first one with the lowest sequence
        user = self.env.user
        groups = self.env["res.users"]._get_implied_groups(user)
        potential_rules = self.env["approval.rule"].find_matching_rules(
            model_name, company.id, groups.ids, action_type
        )

        # Then we try to create new approval requests for the grouped records
        # we only create for those which already don't have one.
        ongoing_request_domain = [
            ("approval_request_ids.request_status", "in", ["new", "pending"]),
        ]
        all_request_records = self.env[model_name].concat(*company_grouped_records)
        ongoing_requests = all_request_records.filtered_domain(ongoing_request_domain)
        if ongoing_requests:
            active_requests = True

        new_request_records = all_request_records - ongoing_requests
        app_requests = potential_rules.create_approval_request(
            model_name, new_request_records, func.__name__
        )

    # If new approval requests were created we need to create activities for
    # pending approvers
    if app_requests:
        approvers = app_requests.approver_ids
        approvers.filtered(lambda x: x.status == "pending")._create_activity()
        app_requests.create_request_status_activity(message_type="create")

    # If everything is ok we will proceed with the original operation
    if not active_requests and not app_requests:
        return func(*args, **kwargs)


@decorator.decorator
def approval_cancel_action(func, *args, **kwargs):
    self = args[0]
    self.approval_request_ids.approver_ids.write({"status": "cancel"})
    self.approval_request_ids.write({"active": False})
    return func(*args, **kwargs)


@decorator.decorator
def approval_pending_message(func, *args, **kwargs):
    self = args[0]
    if self.approval_request_ids.filtered(lambda x: x.request_status == "pending"):
        raise UserError(
            _(
                "You can't perform action or change the values, "
                "when there is an Approval request in status pending."
            )
        )

    return func(*args, **kwargs)


class ApprovalRule(models.Model):
    _name = "approval.rule"
    _description = "Approval Rule"

    def _approval_category_domain(self):
        return [
            ("is_advanced", "=", True),
        ]

    name = fields.Text(required=True)
    model_id = fields.Many2one(
        comodel_name="ir.model",
        domain=lambda x: x._get_model_id_domain(),
        index=True,
        required=True,
        ondelete="cascade",
    )
    group_ids = fields.Many2many(comodel_name="res.groups", string="Security Roles")
    domain = fields.Char(
        string="Filter", compute="_compute_domain", readonly=False, store=True
    )
    model_name = fields.Char(
        string="Model Name", related="model_id.model", readonly=True, store=True
    )
    approval_category_id = fields.Many2one(
        comodel_name="approval.category",
        required=True,
        index=True,
        ondelete="restrict",
        domain="[('is_advanced', '=', True), '|', ('company_id', '=', False), "
        "('company_id', '=', company_id)]",
        company_dependent=False,
    )
    company_id = fields.Many2one(comodel_name="res.company")
    action_type = fields.Selection(
        selection=[("confirm", "Confirm"), ("send_by_mail", "Send by Mail")],
        default="confirm",
        required=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=1)
    approval_category_id_companies = fields.One2many(
        comodel_name="res.company", compute="_compute_approval_category_id_companies"
    )
    automatic_document_confirmation = fields.Boolean(
        default=True,
    )
    override_group_ids = fields.Many2many(
        comodel_name="res.groups", relation="override_group_rule_rel"
    )

    def _get_model_id_domain(self):
        return [("approval_request_link", "=", True)]

    @api.depends("model_id")
    def _compute_domain(self):
        for rule in self:
            if rule._origin.model_id != rule.model_id:
                rule.domain = repr([])
            else:
                rule.domain = rule.domain

    @api.onchange("company_id")
    def _onchange_company_id(self):
        self.approval_category_id = (
            False
            if self._origin.company_id != self.company_id
            else self.approval_category_id
        )

    @api.model
    def find_matching_rules(self, model_name, company_id, group_ids, action_type):
        """
        Searching for potential rules to be triggered when an action is called
        on an object
        :param model_name: model name of the object from which it was called
        :param company_id: company of the object
        :param group_ids: filter rules by user groups if specified on rule
        :param action_type: type of the action that was triggered on the object
        :return: all matched rules ordered by sequence
        """
        return self.sudo().search(
            [
                ("model_id", "=", model_name),
                "|",
                ("company_id", "=", company_id),
                ("company_id", "=", False),
                "|",
                (
                    "group_ids",
                    "in",
                    group_ids,
                ),
                ("group_ids", "=", False),
                ("action_type", "=", action_type),
                ("approval_category_id", "!=", False),
            ],
            order="sequence",
        )

    def create_approval_request(
        self,
        model_name,
        new_request_records,
        approval_method_name,
    ):
        used_request_records = self.env[model_name]
        app_requests = self.env["approval.request"]

        new_request_records_wo_domain = new_request_records

        for potential_rule in self:
            new_request_records = new_request_records_wo_domain
            new_request_domain = [
                ("approval_request_ids.request_status", "!=", "approved"),
                ("approval_request_ids.approval_rule_id", "!=", potential_rule.id),
            ]
            new_request_domain.extend(literal_eval(potential_rule.domain))
            new_request_records = new_request_records.filtered_domain(
                new_request_domain
            )
            new_request_records -= used_request_records

            for rec in new_request_records:
                used_request_records |= rec
                approver_line_vals = (
                    potential_rule.approval_category_id.generate_approver_lines(
                        potential_rule.model_name
                    )
                )

                same_request_rules = rec.with_context(
                    active_test=False
                ).approval_request_ids.filtered(
                    lambda x: x.approval_rule_id == potential_rule
                )

                request_counter = (
                    len(same_request_rules) + 1 if same_request_rules else 1
                )
                values = potential_rule._prepare_request_values(
                    model_name,
                    rec,
                    request_counter,
                    approver_line_vals,
                    approval_method_name,
                    rec.state,
                )

                app_requests |= app_requests.sudo().create(values)

        return app_requests

    def _prepare_request_values(
        self,
        model_name,
        src_document,
        req_counter,
        approver_line_vals,
        approval_method_name,
        approval_model_state,
    ):
        self.ensure_one()
        return {
            "name": "Request %s for Rule - %s #%s"
            % (
                src_document.name,
                self.name,
                req_counter,
            ),
            "category_id": self.approval_category_id.id,
            "request_owner_id": self.env.user.id,
            "source_document": "% s,% s" % (model_name, src_document.id),
            "res_model": "%s" % model_name,
            "res_id": "%s" % src_document.id,
            "date_confirmed": fields.Datetime.now(),
            "max_approval_line": len(
                {x[2]["matrix_line_id"] for x in approver_line_vals}
            ),
            "approval_rule_id": self.id,
            "approver_ids": approver_line_vals,
            "approval_method_name": approval_method_name,
            "approval_model_state": approval_model_state,
        }

    def _can_override_approval(self):
        self.ensure_one()

        overide_groups = ",".join(self.override_group_ids.get_external_id().values())
        return overide_groups and self.user_has_groups(overide_groups)
