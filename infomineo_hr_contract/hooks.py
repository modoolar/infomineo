from collections import defaultdict

from odoo import api

from odoo.addons.hr_contract.report.hr_contract_history import ContractHistory


@api.depends("employee_id.contract_ids")
def _compute_contract_ids(self):
    sorted_contracts = self.mapped("employee_id.contract_ids").sorted(
        "date_start", reverse=True
    )

    mapped_employee_contracts = defaultdict(lambda: self.env["hr.contract"])
    for contract in sorted_contracts:
        mapped_employee_contracts[contract.employee_id] |= contract

    for history in self:
        history.contract_ids = mapped_employee_contracts[history.employee_id]


def post_load():
    ContractHistory._patch_method("_compute_contract_ids", _compute_contract_ids)
