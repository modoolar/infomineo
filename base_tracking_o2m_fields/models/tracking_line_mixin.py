# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import _, models


class TrackingLineMixin(models.AbstractModel):
    _name = "tracking.line.mixin"
    _description = "Tracking Line Mixin"

    def write(self, vals):
        parent_fields = (
            self._parent_tracking_fields
            if hasattr(self, "_parent_tracking_fields")
            else list()
        )

        if not parent_fields:
            return super().write(vals)

        if not self.env.context.get("tracking_disable", False):
            tracking_fields_list = self.get_tracking_fields()

            tracking_fields = self.fields_get(tracking_fields_list)

            initial_values = {}
            for line in self:
                for field_name in tracking_fields_list:
                    for parent_field in parent_fields:
                        if line[parent_field].id not in initial_values:
                            initial_values[line[parent_field].id] = {}
                        initial_values[line[parent_field].id].update(
                            {field_name: line[field_name]}
                        )

        result = super().write(vals)

        if not self.env.context.get("tracking_disable", False):
            for parent_field_id, modified_lines in initial_values.items():
                for parent_field in parent_fields:
                    for line in self.filtered(
                        lambda l: l[parent_field].id == parent_field_id
                    ):
                        tracking_value_ids = line._mail_track(
                            tracking_fields, modified_lines
                        )[1]
                        if tracking_value_ids:
                            msg = _(
                                "Line %s updated",
                                line._get_html_link(title=f"#{line.id}"),
                            )
                            line[parent_field]._message_log(
                                body=msg, tracking_value_ids=tracking_value_ids
                            )

        return result

    def get_tracking_fields(self):
        """Hook method for other modules to use to get tracking fields."""
        return list()
