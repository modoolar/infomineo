# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    project_sequence_id = fields.Many2one(
        comodel_name="ir.sequence", index=True, readonly=True
    )

    def get_next_project_sequence(self):
        self.ensure_one()

        if not self.project_sequence_id:
            self._create_project_sequence()

        return self.project_sequence_id.next_by_id()

    def _create_project_sequence(self):
        self.ensure_one()
        self.project_sequence_id = (
            self.env["ir.sequence"].sudo().create(self._prepare_project_sequence_data())
        )

    def _prepare_project_sequence_data(self):
        self.ensure_one()

        return {
            "name": "{} {}".format(self.name, _("Project sequence")),
            "implementation": "standard",
            "code": f"res.partner.project.sequence.code.{self.id}",
            "prefix": "00",
            "padding": 2,
            "use_date_range": False,
            "number_increment": 1,
            "number_next_actual": 1,
        }

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get("sudo_create_partner", False):
            ctx = dict(self._context)
            ctx.pop("default_parent_id", None)

            return super(ResPartner, self.with_context(ctx).sudo()).create(vals_list)
        return super().create(vals_list)
