# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class EBDSSortantLine(models.Model):
    _name = "e_bds.sortant.line"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    situation = fields.Selection(
        selection=[
            ("SO", "Sortant"),
            ("DE", "Decédé"),
            ("IT", "Maternité"),
            ("IL", "Maladie"),
            ("AT", "Accident de Travail"),
            ("CS", "Congé Sans salaire"),
            ("MS", "Maintenu Sans Salaire"),
            ("MP", "Maladie Professionnelle"),
        ]
    )
    e_bds_sortant_id = fields.Many2one("e_bds.sortant", "e_bds_sortant")
