# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api

from odoo.addons.account.models.account_analytic_default import (
    AccountAnalyticDefault as originalAccountAnalyticDefault,
)


@api.model
def account_get(
    self,
    product_id=None,
    partner_id=None,
    account_id=None,
    user_id=None,
    date=None,
    company_id=None,
    department_id=False,
):
    domain = []
    if product_id:
        domain += ["|", ("product_id", "=", product_id)]
    domain += [("product_id", "=", False)]
    if partner_id:
        domain += ["|", ("partner_id", "=", partner_id)]
    domain += [("partner_id", "=", False)]
    if account_id:
        domain += ["|", ("account_id", "=", account_id)]
    domain += [("account_id", "=", False)]
    if company_id:
        domain += ["|", ("company_id", "=", company_id)]
    domain += [("company_id", "=", False)]
    if user_id:
        domain += ["|", ("user_id", "=", user_id)]
    domain += [("user_id", "=", False)]
    if department_id:
        domain += ["|", ("department_id", "=", department_id)]
    domain += [("department_id", "=", False)]
    if date:
        domain += ["|", ("date_start", "<=", date), ("date_start", "=", False)]
        domain += ["|", ("date_stop", ">=", date), ("date_stop", "=", False)]

    return get_best_result_match(self, domain)


def get_best_result_match(self, domain):
    res = self.env["account.analytic.default"]
    best_index = -1

    for rec in self.search(domain):
        index = 0
        if rec.product_id:
            index += 1
        if rec.partner_id:
            index += 1
        if rec.account_id:
            index += 1
        if rec.company_id:
            index += 1
        if rec.user_id:
            index += 1
        if rec.department_id:
            index += 1
        if rec.date_start:
            index += 1
        if rec.date_stop:
            index += 1
        if index > best_index:
            res = rec
            best_index = index
    return res


def patch_account_analytic_default_methods():
    originalAccountAnalyticDefault._patch_method("account_get", account_get)
