# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import groupby

APPROVER_PRIORITY_LEVELS = ["AVAILABLE", "UNAVAILABLE"]


class AdvancedApprovalCategoryApprover(models.Model):
    _name = "advanced.approval.category.approver"
    _order = "sequence"
    _description = "Advanced Approval Category Approver"
    _rec_name = "common_name"

    category_id = fields.Many2one(
        comodel_name="approval.category", index=True, required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=1)
    approval_authorization_level_id = fields.Many2one(
        comodel_name="approval.authorization.level", required=True, ondelete="restrict"
    )
    minimum_approvals = fields.Integer(required=True, default=1)
    use_employee_manager = fields.Boolean(string="Employee's Manager")
    use_employee_department = fields.Boolean()
    other_department_ids = fields.Many2many(comodel_name="hr.department")
    common_name = fields.Char(compute="_compute_common_name", store=True)
    category_ids = fields.Many2many(
        comodel_name="hr.employee.category", string="Employee Tags"
    )
    use_employee_tags = fields.Boolean(
        compute="_compute_use_employee_tags", inverse="_inverse_use_employee_tags"
    )
    company_ids = fields.Many2many(comodel_name="res.company")

    @api.depends("approval_authorization_level_id")
    def _compute_common_name(self):
        for advanced_line in self:
            advanced_line.common_name = (
                advanced_line.approval_authorization_level_id.display_name
            )

    @api.depends("category_ids")
    def _compute_use_employee_tags(self):
        for rec in self:
            rec.use_employee_tags = bool(rec.category_ids)

    def _inverse_use_employee_tags(self):
        lines_with_tags = self.filtered(lambda x: x.category_ids)
        lines_with_tags.use_employee_department = False
        lines_with_tags.other_department_ids = False

    @api.model_create_multi
    def create(self, vals_list):
        for category_id, vals_groupedby_category in groupby(
            vals_list, lambda x: x["category_id"]
        ):
            max_seq_approver = self.search(
                [("category_id", "=", category_id), ("sequence", "!=", False)],
                order="sequence desc",
                limit=1,
            )

            default_sequence = max_seq_approver.sequence if max_seq_approver else 0

            for vals in vals_groupedby_category:
                default_sequence += 1
                vals["sequence"] = default_sequence

        return super().create(vals_list)

    def get_selected_approvers(
        self,
        invoked_from_model,
        user_employee=None,
        use_unavailable=False,
        exclude_user_ids=None,
        required_approvers=1,
        raise_if_not_found=True,
    ):
        if exclude_user_ids is None:
            exclude_user_ids = []
        self.ensure_one()
        if not user_employee:
            user_employee = self.env.user.employee_id

        selected_approvers = self.env["hr.employee"]
        res_users = self.env["res.users"]

        # By priority if we check `use employee manager`
        # We need to add his manager to selected approvers.
        # Manager is a `res.users` field on employee.
        manager_approver = self._get_employee_manager(user_employee)

        if manager_approver and manager_approver.id not in exclude_user_ids:
            manager_has_access = self.env["ir.model.access"].check_group(
                invoked_from_model,
                "read",
                res_users._get_implied_groups(manager_approver).ids,
            )
            if not manager_has_access:
                raise UserError(
                    _(
                        "Your Manager doesn't have access to this document, "
                        "please add the Manager to security group to see this "
                        "document or Contact System Administrator."
                    )
                )

            exclude_user_ids.append(manager_approver.id)
            required_approvers -= 1
        if required_approvers == 0:
            return manager_approver

        # From now on we will check for additional buffer if filled
        # for CRON we will not add buffer
        if not self._context.get("initiated_by_cron"):
            additional_buffer = self.env.company.additional_approver_buffer
            required_approvers += additional_buffer
        else:
            additional_buffer = 0
        # We need to group by all candidate employees for a particular level
        # which can be approvers by the department they're in.
        exclude_user_ids.append(user_employee.user_id.id)
        exclude_user_ids.extend(selected_approvers.mapped("user_id").ids)

        candidates_domain, candidates_department_priority = self._get_candidates_domain(
            user_employee, exclude_user_ids
        )
        all_candidate_approvers = self.env["hr.employee"].read_group(
            domain=candidates_domain,
            fields=["department_id", "ids:array_agg(id)"],
            groupby=["department_id"],
            lazy=False,
        )

        all_candidate_approvers_data = {
            x["department_id"][0]: self.filter_candidates(x["ids"])
            for x in all_candidate_approvers
            if x["department_id"]
        }
        if len(candidates_department_priority) == 0:
            candidates_department_priority = list(all_candidate_approvers_data.keys())

        # After we get all candidates grouped by departments
        # We will go through all priorities and filter each department
        # and take candidates from it.
        for priority_lvl in APPROVER_PRIORITY_LEVELS:
            if not use_unavailable and priority_lvl == "UNAVAILABLE":
                continue

            for department in candidates_department_priority:
                filtered_candidates = all_candidate_approvers_data.get(
                    department, dict()
                )
                if filtered_candidates and filtered_candidates.get(priority_lvl):
                    candidates = filtered_candidates.get(priority_lvl)
                    if any(x for x in candidates if not x.user_id):
                        raise UserError(
                            _("Some candidates don't have a linked user to them.")
                        )

                    candidates = candidates.filtered(
                        lambda x: x.id not in selected_approvers.ids
                        and self.env["ir.model.access"].check_group(
                            invoked_from_model,
                            "read",
                            res_users._get_implied_groups(x.user_id).ids,
                        )
                    )
                    if required_approvers <= len(candidates):
                        selected_approvers |= candidates[:required_approvers]
                        return manager_approver | selected_approvers.get_linked_users()
                    else:
                        selected_approvers |= candidates.filtered(
                            lambda x: x.id not in selected_approvers.ids
                        )
                        required_approvers -= len(candidates)

        # We didn't find enough candidates, so we are going to check
        # whether we have enough without the buffer if we do we will
        # return them (buffer is optional)
        if (required_approvers - additional_buffer) <= 0:
            return manager_approver | selected_approvers.get_linked_users()
        if raise_if_not_found:
            raise UserError(
                _(
                    "There aren't enough approvers for your request. Either modify "
                    "the document to avoid the rule and try again, or contact the "
                    "System Administrator."
                )
            )
        return self.env["res.users"]

    def _get_employee_manager(self, user_employee):
        self.ensure_one()

        if self.use_employee_manager:
            if user_employee.approval_manager_id:
                return user_employee.approval_manager_id
            else:
                raise UserError(
                    _(
                        "Approval Category: %s requires you to"
                        " have an Employee Manager."
                    )
                    % self.category_id.name
                )

        return self.env["res.users"]

    def _get_candidates_domain(self, user_employee, exclude_user_ids=None):
        if exclude_user_ids is None:
            exclude_user_ids = []

        self.ensure_one()
        candidates_domain = [
            (
                "approval_authorization_level_id",
                "=",
                self.approval_authorization_level_id.id,
            ),
            (
                "user_id",
                "not in",
                exclude_user_ids,
            ),
        ]
        candidates_domain_extra = []
        priority_domain = []
        if self.company_ids:
            candidates_domain = expression.AND(
                [
                    candidates_domain,
                    [("user_id.company_id", "in", self.company_ids.ids)],
                ]
            )
        if self.use_employee_department:
            candidates_domain_extra = expression.OR(
                [
                    candidates_domain_extra,
                    [("department_id", "=", user_employee.department_id.id)],
                ]
            )
            priority_domain.append(user_employee.department_id.id)
        if self.use_employee_department and self.env.company.include_parent_departments:
            candidates_domain_extra = expression.OR(
                [
                    candidates_domain_extra,
                    [("department_id", "=", user_employee.department_id.parent_id.id)],
                ]
            )
            priority_domain.append(user_employee.department_id.parent_id.id)
        if self.other_department_ids:
            candidates_domain_extra = expression.OR(
                [
                    candidates_domain_extra,
                    [("department_id", "in", self.other_department_ids.ids)],
                ]
            )
            priority_domain.extend(self.other_department_ids.ids)
        if self.other_department_ids and self.env.company.include_parent_departments:
            candidates_domain_extra = expression.OR(
                [
                    candidates_domain_extra,
                    [
                        (
                            "department_id",
                            "in",
                            self.mapped("other_department_ids.parent_id").ids,
                        )
                    ],
                ]
            )
            priority_domain.extend(self.mapped("other_department_ids.parent_id").ids)
        if self.category_ids:
            candidates_domain_extra = expression.OR(
                [
                    candidates_domain_extra,
                    [("category_ids", "in", self.category_ids.ids)],
                ]
            )
        candidates_domain = expression.AND([candidates_domain, candidates_domain_extra])

        return candidates_domain, priority_domain

    def filter_candidates(self, candidate_ids):
        """
        Hook method for other modules to filter candidates.
        It will return candidates grouped in `APPROVER_PRIORITY_LEVELS` levels.
        """
        candidates = list(self.env["hr.employee"].browse(candidate_ids))
        random.shuffle(candidates)
        return {
            k: self.env["hr.employee"].concat(*candidates)
            if k == "AVAILABLE"
            else list()
            for k in APPROVER_PRIORITY_LEVELS
        }

    @api.model
    def sort_candidates(self, candidates):
        """
        Hook method for other modules to sort candidates.
        It will return candidates grouped in `APPROVER_PRIORITY_LEVELS` levels.
        The candidates should be prioritized from best to worst candidate
        in all groups.
        """

        return candidates

    @api.constrains("minimum_approvals")
    def _check_minimum_approvals(self):
        for rec in self:
            if rec.minimum_approvals < 1:
                raise UserError(_("Minimum Approvals value must be greater than 0."))

    @api.constrains("use_employee_manager")
    def _check_one_manager(self):
        for rec in self:
            if (
                len(
                    rec.category_id.advanced_approver_ids.filtered(
                        lambda x: x.use_employee_manager
                    )
                )
                > 1
            ):
                raise UserError(_("Only one line can have Use Manager."))
