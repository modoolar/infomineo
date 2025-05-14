# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
import random

from odoo import fields, models

from odoo.addons.approvals_matrix.models.advanced_approval_category_approver import (
    APPROVER_PRIORITY_LEVELS,
)

APPROVER_PRIORITY_LEVELS += [
    "TIME_OFF_UNAVAILABLE",
]


class AdvancedApprovalCategoryApprover(models.Model):
    _inherit = "advanced.approval.category.approver"

    def filter_candidates(self, candidate_ids):
        candidates = self.env["hr.employee"].browse(candidate_ids)
        filtered_candidates = dict()

        for k in APPROVER_PRIORITY_LEVELS:
            if k == "AVAILABLE":
                available_candidates = list(
                    candidates.filtered_domain([("is_absent", "!=", True)])
                )
                random.shuffle(available_candidates)
                filtered_candidates[k] = self.env["hr.employee"].concat(
                    *available_candidates
                )
            if k == "TIME_OFF_UNAVAILABLE":
                filtered_candidates[k] = self.sort_candidates(
                    candidates.filtered_domain([("is_absent", "=", True)])
                )

        return filtered_candidates

    def sort_candidates(self, candidates):
        return candidates.sorted(lambda x: x.leave_date_to - fields.Date.today())
