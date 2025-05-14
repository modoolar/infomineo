# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class MailTrackingValue(models.Model):
    _inherit = "mail.tracking.value"

    def create_tracking_values(
        self,
        initial_value,
        new_value,
        col_name,
        col_info,
        tracking_sequence,
        model_name,
    ):
        res = super().create_tracking_values(
            initial_value, new_value, col_name, col_info, tracking_sequence, model_name
        )
        if res:
            return res

        field = self.env["ir.model.fields"]._get(model_name, col_name)
        if not field:
            return

        values = {
            "field": field.id,
            "field_desc": col_info["string"],
            "field_type": col_info["type"],
            "tracking_sequence": tracking_sequence,
        }

        if col_info["type"] in ["one2many", "many2many"]:
            values.update(
                {
                    "old_value_%s" % col_info["type"]: initial_value,
                    "new_value_%s" % col_info["type"]: new_value,
                }
            )
