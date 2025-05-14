# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models

from odoo.addons.planning.models.planning import Planning
from odoo.addons.sale_planning.models.planning_slot import PlanningSlot


class PlanningSlotTest(models.Model):
    _inherit = "planning.slot"

    def _compute_allocated_hours(self):
        return PlanningSlot._compute_allocated_hours(self)

    def _get_slot_duration(self):
        return Planning._get_slot_duration(self)
