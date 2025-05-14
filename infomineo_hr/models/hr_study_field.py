# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class HrStudyField(models.Model):
    _name = "hr.study.field"
    _description = "HR Study Field"

    name = fields.Char(index=True)
    is_active = fields.Boolean(default=True)
