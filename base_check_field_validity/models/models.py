# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    def check_field_validity(self, f_name, valid_value=None, vals=None):
        """
        Checks whether a field is valid. It's used in create or write methods.
        It will check the field's name in the vals and if it doesn't find it
        it will check in `self` for it.
        :param f_name: field name
        :param valid_value: value to which the f_value is being compared
        :param vals: dictionary of values that are being changed, which might
        or might not contain the f_name
        :return: Boolean value if the f_name is valid or not
        """
        if vals is None:
            vals = {}
        f_value = vals.get(f_name)
        if not f_value and self[f_name]:
            self.ensure_one()
            f_value = self[f_name]

        return self._is_value_valid(f_value, valid_value)

    @api.model
    def _is_value_valid(self, f_value, valid_value=None):
        """
        Checks whether a field_value is populated if valid_value is None
        or if field_value is equal to valid_value if valid_value is populated.
        :param f_value: value of a field
        :param valid_value: value to which the f_value is being compared
        :return: Boolean value if the f_value is valid or not
        """
        if not f_value:
            return False

        return f_value == valid_value if valid_value else f_value
