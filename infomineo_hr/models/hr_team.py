# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrTeam(models.Model):
    _name = "hr.team"
    _description = "HR Team"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "name"
    _order = "complete_name"

    name = fields.Char(index=True)
    is_active = fields.Boolean(default=True)
    parent_id = fields.Many2one(
        "hr.team", "Parent Team", index=True, ondelete="cascade"
    )
    child_id = fields.One2many("hr.team", "parent_id", "Child Teams")
    parent_path = fields.Char(index=True)
    complete_name = fields.Char(
        "Complete Name", compute="_compute_complete_name", recursive=True, store=True
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for team in self:
            if team.parent_id:
                team.complete_name = "%s / %s" % (
                    team.parent_id.complete_name,
                    team.name,
                )
            else:
                team.complete_name = team.name

    @api.constrains("parent_id")
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive categories."))
