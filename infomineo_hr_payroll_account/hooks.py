from .substitutions.account_analytic_default import (
    patch_account_analytic_default_methods,
)
from .substitutions.account_move_line import patch_account_move_line_methods
from .substitutions.hr_payslip import patch_hr_payslip_methods


def post_load():
    patch_account_move_line_methods()
    patch_account_analytic_default_methods()
    patch_hr_payslip_methods()
