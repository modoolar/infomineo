# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    approval_request_link = fields.Boolean()
    blacklisted_fields = fields.Char()

    def _reflect_model_params(self, model):
        vals = super()._reflect_model_params(model)
        vals["approval_request_link"] = hasattr(model, "_approval_request_link")
        return vals
