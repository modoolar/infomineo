# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import models


class ResUsers(models.Model):  # pragma: no cover
    _inherit = "res.users"

    def create(self, vals_list):
        """
        This extensions is here to enable proper execution tests
        related to access of Purchase Orders
        """

        users = super().create(vals_list)
        users.add_purchase_order_all_role()
        return users

    def add_purchase_order_all_role(self):
        """
        Adding  role to user with login 'accountman'
        """
        users = self.filtered(
            lambda x: self.env.ref("purchase.group_purchase_user") in x.groups_id
        )
        if users:
            users.groups_id += self.env.ref(
                "infomineo_purchase.group_all_purchase_orders"
            )
