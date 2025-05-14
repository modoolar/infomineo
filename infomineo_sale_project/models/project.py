# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    deal_name = fields.Char(
        related="sale_order_id.description", readonly=False, store=True
    )
    contact_id = fields.Many2one(
        domain="["
        "('parent_id', '=', partner_id),"
        " ('company_id', '=', False),"
        " ('type', '=', 'contact')"
        "]"
    )
    specific_conditions = fields.Html(
        related="sale_order_id.specific_condition", translate=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        self._set_client_project_type(vals_list)
        self._set_project_auto_name(vals_list)

        return super().create(vals_list)

    def write(self, vals):
        if isinstance(vals.get("partner_id"), int):
            self._set_project_auto_name(vals)

        return super().write(vals)

    @api.model
    def _set_client_project_type(self, vals_list):
        for vals in vals_list:
            if vals.get("sale_line_id", False):
                vals.update({"project_type": "client"})

    @api.model
    def _set_project_auto_name(self, vals):
        if isinstance(vals, dict):
            vals.update(
                {"name": self._generate_project_name(vals.get("partner_id", False))}
            )
            return

        for value in vals:
            value.update(
                {"name": self._generate_project_name(value.get("partner_id", False))}
            )

    @api.model
    def _generate_project_name(self, client_id):
        client = self.env["res.partner"].browse(client_id)
        template = "{client_ref}/{project_ref}"

        if client:
            client_ref = client.ref
            project_ref = client.get_next_project_sequence()
        else:
            client_ref = "00"
            project_ref = self.env["ir.sequence"].next_by_code(
                "infomineo_sale_project.internal_project_number"
            )

        return template.format(client_ref=client_ref, project_ref=project_ref)
