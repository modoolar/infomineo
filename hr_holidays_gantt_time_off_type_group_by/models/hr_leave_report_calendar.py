# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import SUPERUSER_ID, _, fields, models, tools


class LeaveReportCalendar(models.Model):
    _inherit = "hr.leave.report.calendar"

    holiday_status_id = fields.Many2one(
        comodel_name="hr.leave.type", string="Time Off Type", readonly=True
    )

    def init(self):
        """
        Override method to include field holiday_status_id
        """
        # TODO duration field isn't in select query so name_get is raising an error.
        # We can patch it by adding that column with something like this:
        # EXTRACT(epoch FROM (hl.date_to - hl.date_from))/3600 AS duration,
        tools.drop_view_if_exists(self._cr, "hr_leave_report_calendar")
        self._cr.execute(
            """CREATE OR REPLACE VIEW hr_leave_report_calendar AS
        (SELECT
            hl.id AS id,
            CONCAT(em.name, ': ', hl.duration_display) AS name,
            hl.date_from AS start_datetime,
            hl.date_to AS stop_datetime,
            hl.employee_id AS employee_id,
            hl.state AS state,
            hl.department_id AS department_id,
            hl.holiday_status_id AS holiday_status_id,
            em.company_id AS company_id,
            em.job_id AS job_id,
            COALESCE(
                CASE WHEN hl.holiday_type = 'employee' THEN COALESCE(rr.tz, rc.tz) END,
                cc.tz,
                'UTC'
            ) AS tz,
            hl.state = 'refuse' as is_striked,
            hl.state not in ('validate', 'refuse') as is_hatched
        FROM hr_leave hl
            LEFT JOIN hr_employee em
                ON em.id = hl.employee_id
            LEFT JOIN resource_resource rr
                ON rr.id = em.resource_id
            LEFT JOIN resource_calendar rc
                ON rc.id = em.resource_calendar_id
            LEFT JOIN res_company co
                ON co.id = em.company_id
            LEFT JOIN resource_calendar cc
                ON cc.id = co.resource_calendar_id
        WHERE
            hl.state IN ('confirm', 'validate', 'validate1')
        );
        """
        )

    def _read(self, fields):
        res = super()._read(fields)
        if self.env.context.get(
            "hide_employee_name"
        ) and "employee_id" in self.env.context.get("group_by", []):
            name_field = self._fields["name"]
            for leave in self.with_user(SUPERUSER_ID):
                leave_type = _("%s") % (leave.holiday_status_id.name,)
                self.env.cache.set(
                    leave, name_field, "%s : %s" % (leave_type, leave.name)
                )
        return res
