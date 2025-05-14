# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group("hr.group_hr_user"):
            res.append(
                self.env.ref("infomineo_hr_attendance.menu_hr_employee_coach").id
            )
        elif self.env.user.has_group("infomineo_hr_attendance.group_hr_coach"):
            res.append(self.env.ref("hr.menu_hr_employee").id)

        return res
