# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Petar Najman <petar.najman@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    REF_DELIMITER = "/"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override in order to postprocess reference
        """
        result = super().create(vals_list)
        result._post_process_ref()
        return result

    @api.onchange("parent_id", "company_type")
    def _onchange_ref_parent_id(self):
        """
        When parent is changed we want to recalculate reference for existing records
        """
        if not self.ref:
            return

        refs = self.ref.split(self.REF_DELIMITER)
        ref = refs[-1]
        if self.company_type == "person":
            ref = f"C{self.REF_DELIMITER}{ref}"
        self.ref = self.parent_id and self._format_ref(ref, self.parent_id.ref) or ref

    def _post_process_ref(self):
        """
        If exists incorporate parent reference
        """
        for partner in self.filtered(lambda x: x.company_type == "person"):
            partner.ref = f"C{self.REF_DELIMITER}{partner.ref}"
        for partner in self.filtered(lambda x: x.parent_id):
            partner.ref = self._format_ref(partner.ref, partner.parent_id.ref)

    @api.model
    def _format_ref(self, ref, parent_ref):
        """
        Format reference number
        """
        return f"{parent_ref}{self.REF_DELIMITER}{ref}"

    @api.model
    def _commercial_fields(self):
        """
        Override to remove "ref" from commercial field list as we want for every
        contact to have its own reference number.
        """
        commercial_fields = super()._commercial_fields()
        if "ref" in commercial_fields:
            commercial_fields.remove("ref")
        return commercial_fields

    def _needs_ref(self, vals=None):
        """
        Trigger validation in parent but we don't care about the result
        as we are always generating reference
        """
        super()._needs_ref(vals=vals)
        return True
