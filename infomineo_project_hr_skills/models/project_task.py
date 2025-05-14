# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    special_language_skill_id = fields.Many2many(
        comodel_name="hr.skill",
        domain=lambda self: self._domain_special_language_skill(),
    )

    def _domain_special_language_skill(self):
        language_skill = self.env.ref(
            "infomineo_project_hr_skills.hr_skill_type_language",
            raise_if_not_found=False,
        )
        return [("skill_type_id", "=", language_skill.id)] if language_skill else []
