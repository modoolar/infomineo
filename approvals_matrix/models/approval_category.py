# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from functools import reduce

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    is_advanced = fields.Boolean(string="Advanced")
    is_advanced_selected = fields.Boolean(
        inverse="_inverse_is_advanced_selected", store=True
    )
    advanced_approver_ids = fields.One2many(
        comodel_name="advanced.approval.category.approver",
        inverse_name="category_id",
        string="Advanced Approvers",
    )
    advanced_approval_minimum = fields.Integer(
        inverse="_inverse_advanced_approval_minimum"
    )
    company_id = fields.Many2one(required=False)

    @api.onchange("advanced_approver_ids")
    def _inverse_advanced_approval_minimum(self):
        for category in self.filtered(lambda x: x.is_advanced):
            approval_lines_minimum = category.mapped(
                "advanced_approver_ids.minimum_approvals"
            )
            category.approval_minimum = (
                sum(approval_lines_minimum) if approval_lines_minimum else 0
            )

    def generate_approver_lines(self, invoked_from_model):
        self.ensure_one()

        approvers_vals = list()

        if not self.advanced_approver_ids:
            raise UserError(
                _("Approval  category %s doesn't have any lines." % self.name)
            )

        if self.advanced_approver_ids:
            minimal_sequence = reduce(
                lambda x, y: min(x, y), self.advanced_approver_ids.mapped("sequence")
            )
        else:
            minimal_sequence = 1000
        excluded_users = self.env["res.users"]
        for advanced_line in self.advanced_approver_ids:
            selected_users = advanced_line.get_selected_approvers(
                invoked_from_model=invoked_from_model,
                use_unavailable=True,
                required_approvers=advanced_line.minimum_approvals,
                exclude_user_ids=excluded_users.ids,
            )

            excluded_users |= selected_users

            approvers_vals.extend(
                [
                    Command.create(
                        {
                            "user_id": user.id,
                            "status": "pending"
                            if advanced_line.sequence == minimal_sequence
                            else "new",
                            "sequence": advanced_line.sequence,
                            "matrix_line_id": advanced_line.id,
                        }
                    )
                    for user in selected_users
                ]
            )

        return approvers_vals

    @api.onchange("is_advanced")
    def _inverse_is_advanced_selected(self):
        default_category = self.new()

        for category in self.filtered(lambda x: x.is_advanced):
            category.update(
                {
                    categ: default_category[categ]
                    for categ in default_category._fields
                    if categ not in self.get_restricted_field_names()
                }
            )

    def get_restricted_field_names(self):
        return ["id", "name", "is_advanced", "sequence_code"]

    @api.constrains("is_advanced", "advanced_approver_ids")
    def _check_valid_category(self):
        """
        Check if all categories that are linked to rules are flaged as advanced.
        """
        approval_rules = (
            self.env["approval.rule"]
            .sudo()
            .search(
                [
                    ("approval_category_id", "in", self.ids),
                ]
            )
        )
        if any(not x.approval_category_id.is_advanced for x in approval_rules):
            raise UserError(
                _(
                    "You can't remove Advanced flag from a Type that"
                    "is linked to an Approval Rule. "
                )
            )
        if any(not x.advanced_approver_ids and x.is_advanced for x in self):
            raise UserError(_("An Advanced Type must have Approval Type Lines."))
