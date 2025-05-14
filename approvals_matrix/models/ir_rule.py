from odoo import api, models, tools
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        res = super()._compute_domain(model_name, mode)
        if mode == "read" and getattr(
            self.env[model_name], "_approval_request_link", False
        ):
            if getattr(self.env[model_name], "_parent_tracking_fields", False):
                parent_field = self.env[model_name]._parent_tracking_fields

                approver_domain = (
                    parent_field + ".approval_request_ids.approver_ids.user_id",
                    "in",
                    self.env.user.ids,
                )
            else:
                approver_domain = (
                    "approval_request_ids.approver_ids.user_id",
                    "in",
                    self.env.user.ids,
                )

            if isinstance(res, list) and len(res):
                res = expression.OR(
                    [
                        res,
                        [approver_domain],
                    ]
                )
            elif isinstance(res, list):
                res = approver_domain

        return res
