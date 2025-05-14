# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    approval_authorization_level_id = fields.Many2one(
        related="user_id.approval_authorization_level_id", store=True
    )
    approval_manager_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_approval_manager_id",
        readonly=False,
        store=True,
    )

    @api.depends("parent_id")
    def _compute_approval_manager_id(self):
        for rec in self:
            rec.approval_manager_id = (
                rec.parent_id.user_id
                if rec.parent_id and rec.parent_id.user_id
                else rec.approval_manager_id
            )

    def get_linked_users(self):
        selected_users = (
            self.env["res.users"].sudo().search([("employee_id", "in", self.ids)])
        )

        if len(self) != len(selected_users):
            raise UserError(
                _("Approvers: %s don't have Users linked to them.")
                % [x.name for x in self if x.user_id not in selected_users]
            )

        return selected_users

    def check_employee_manager(self):
        employees_without_manager = self.search([("approval_manager_id", "=", False)])
        if employees_without_manager:
            channel = self.env.ref("approvals_matrix.channel_approvals_hr")

            message = employees_without_manager._get_no_manager_message()
            channel.message_post(
                body=message,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )

        return employees_without_manager

    def _get_no_manager_message(self):
        return ("Please set employees Manager on these employees: %s") % (
            self.mapped("name")
        )

    def write(self, vals):
        if (
            "approval_authorization_level_id" in vals
            and vals["approval_authorization_level_id"]
        ):
            no_users = self.filtered(lambda x: not x.user_id)
            if no_users:
                raise UserError(
                    _(
                        "You need to link a User to Employee/s: %s"
                        " if you want to set an Authorization Level"
                    )
                    % (no_users.mapped("name"))
                )

        return super().write(vals)
