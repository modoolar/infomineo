# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ApprovalMatrixMixin(models.AbstractModel):
    _name = "approval.matrix.mixin"
    _inherit = ["tracking.line.mixin"]
    _description = "Approval Matrix Mixin"

    def get_domain(self):
        return [("res_model", "=", self._name)]

    approval_request_ids = fields.One2many(
        comodel_name="approval.request",
        inverse_name="res_id",
        string="Approvals",
        domain=lambda x: x.get_domain(),
    )
    request_status = fields.Selection(
        string="Approval Request Status",
        selection=[
            ("new", "To Submit"),
            ("pending", "Submitted"),
            ("approved", "Approved"),
            ("refused", "Refused"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_request_fields",
        default="new",
        store=True,
    )
    active_request_count = fields.Integer(
        compute="_compute_request_fields", store=False, compute_sudo=True
    )
    archived_request_count = fields.Integer(
        compute="_compute_request_fields", store=False, compute_sudo=True
    )
    request_status_banner = fields.Html(
        compute="_compute_request_fields", store=False, compute_sudo=True
    )

    @api.depends("approval_request_ids", "approval_request_ids.request_status")
    def _compute_request_fields(self):
        for rec in self:
            rec.active_request_count = len(
                rec.with_context(active_test=False).approval_request_ids
            )
            rec.archived_request_count = len(
                rec.with_context(active_test=False).approval_request_ids
                - rec.approval_request_ids
            )
            rec.set_request_status()
            rec.set_request_status_banner()

    def set_request_status(self):
        self.ensure_one()

        if any(
            status == "pending"
            for status in self.mapped("approval_request_ids.request_status")
        ):
            self.request_status = "pending"
        elif any(
            status == "approved"
            for status in self.mapped("approval_request_ids.request_status")
        ):
            self.request_status = "approved"
        elif all(
            status == "refused"
            for status in self.mapped("approval_request_ids.request_status")
        ):
            self.request_status = "refused"
        elif all(
            status == "cancel"
            for status in self.mapped("approval_request_ids.request_status")
        ):
            self.request_status = "cancel"
        else:
            self.request_status = "new"

    def set_request_status_banner(self):
        self.ensure_one()
        if self.request_status == "pending":
            self.request_status_banner = Markup(
                """
                <div class="clearfix"/>
                <div class="alert alert-%s mb-0 text-center w-100"
                role="alert" attrs="{'invisible': [('request_status', '!=', 'pending')]}">
                    <strong>%s</strong>
                </div>
            """
                % (
                    self.request_status,
                    self.request_status.upper(),
                )
            )
        else:
            self.request_status_banner = ""

    def action_view_approvals(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "approvals.approval_request_action"
        )
        approval_request_ids = self.with_context(
            active_test=False
        ).approval_request_ids.ids
        if len(approval_request_ids) == 1:
            approval_request = approval_request_ids[0]
            action["res_id"] = approval_request
            action["view_mode"] = "form"
            action["views"] = [
                (self.env.ref("approvals.approval_request_view_form").id, "form")
            ]
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", approval_request_ids)]

        context = dict(self._context)
        context["active_test"] = False
        action["context"] = context
        return action

    def write(self, vals):
        ongoing_requests = self.env["approval.request"]
        parent_field = (
            self._parent_tracking_fields
            if hasattr(self, "_parent_tracking_fields")
            else ""
        )
        if parent_field:
            ongoing_requests |= self[parent_field].approval_request_ids.filtered(
                lambda x: x.request_status in ["new", "pending", "approved"]
            )
        else:
            ongoing_requests |= self.approval_request_ids.filtered(
                lambda x: x.request_status in ["new", "pending", "approved"]
            )

        can_edit_blacklisted_fields = self.env.user.has_group(
            "approvals_matrix.group_can_edit_approval_request_blacklisted_fields"
        )
        blacklisted_fields = self._get_blacklisted_fields()

        if (
            ongoing_requests
            and list(blacklisted_fields & set(vals.keys()))
            and not can_edit_blacklisted_fields
        ):
            raise UserError(
                _(
                    "You can't perform action or change the values, "
                    "when Approval request in status submitted or approved."
                )
            )
        else:
            return super().write(vals)

    def get_tracking_fields(self):
        return self._get_blacklisted_fields()

    def _get_blacklisted_fields(self):
        current_model = (
            self.env["ir.model"]
            .sudo()
            .search(
                [
                    ("approval_request_link", "=", True),
                    ("model", "=", self._name),
                ]
            )
        )
        return (
            set(current_model.blacklisted_fields.split(","))
            if current_model.blacklisted_fields
            else set()
        )

    def _can_edit_blacklisted_fields(self):
        return self.env.user.has_group(
            "approvals_matrix.group_can_edit_approval_request_blacklisted_fields"
        )

    def unlink(self):
        linked_approvals = self.approval_request_ids
        linked_approvals.unlink()
        return super().unlink()
