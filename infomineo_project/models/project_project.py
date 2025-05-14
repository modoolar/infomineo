# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "rating.mixin"]

    project_director_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('share', '=', False)]",
        string="Project Directors",
    )
    other_project_managers_ids = fields.Many2many(
        comodel_name="res.users",
        relation="project_managers_rel",
        domain="[('share', '=', False)]",
        string="Other Project Managers",
    )
    project_users_ids = fields.Many2many(
        comodel_name="res.users",
        relation="project_users_rel",
        domain="[('share', '=', False)]",
        string="Project Users",
    )
    project_team_members_ids = fields.Many2many(
        compute="_compute_team_members",
        comodel_name="res.users",
        string="Project Team Members",
        search="_search_project_team_members",
    )
    project_type = fields.Selection(
        selection=[
            ("client", "Client"),
            ("internal_strategic", "Internal - strategic"),
            ("internal", "Internal - non strategic"),
        ],
        index=True,
    )
    prevent_task_creation = fields.Boolean()
    actual_end_date = fields.Datetime(tracking=True)
    next_task_number_sequence_id = fields.Many2one(
        comodel_name="ir.sequence", index=True
    )
    next_task_number = fields.Integer(
        related="next_task_number_sequence_id.number_next_actual",
        readonly=False,
        store=False,
    )

    hr_team_id = fields.Many2one(
        comodel_name="hr.team",
        compute="_compute_hr_team_id",
        store=True,
        compute_sudo=True,
    )
    hr_child_team_id = fields.Many2one(
        comodel_name="hr.team",
        compute="_compute_hr_team_id",
        store=True,
        compute_sudo=True,
    )
    customer_recipient_id = fields.Many2one(comodel_name="res.partner", index=True)
    description_mandatory = fields.Boolean()

    @api.depends(
        "user_id",
        "user_id.employee_ids",
        "user_id.employee_ids.hr_team_id",
        "user_id.employee_ids.hr_child_team_id",
    )
    def _compute_hr_team_id(self):
        for rec in self:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", rec.user_id.id)], limit=1
            )
            if employee:
                rec.hr_team_id = employee.hr_team_id
                rec.hr_child_team_id = employee.hr_child_team_id

    @api.depends(
        "user_id",
        "project_director_id",
        "other_project_managers_ids",
        "project_users_ids",
    )
    def _compute_team_members(self):
        for rec in self:
            users = self.env["res.users"]
            users |= rec.user_id
            users |= rec.project_director_id
            users |= rec.other_project_managers_ids
            users |= rec.project_users_ids
            rec.project_team_members_ids = users

    def cron_update_project_state_closing(self):
        closing_stage = self.env["project.project.stage"].search(
            [("is_closed", "=", True)], limit=1
        )
        if not closing_stage:
            return
        projects = self.search(
            [
                ("stage_id", "not in", closing_stage.ids),
                ("package_expiry_datetime", "<", fields.Datetime.now()),
            ]
        )
        projects.write({"stage_id": closing_stage.id})

    def _search_project_team_members(self, operator, value):
        project_ids = self.search(
            [
                "|",
                "|",
                ("project_director_id", operator, value),
                ("other_project_managers_ids", operator, value),
                ("project_users_ids", operator, value),
            ]
        )
        return [("id", "in", project_ids.ids)]

    def write(self, vals):
        stage = self.env["project.project.stage"].browse([vals.get("stage_id", False)])
        if stage and stage.is_closed:
            vals["actual_end_date"] = fields.Datetime.now()

        result = super().write(vals)

        if "stage_id" in vals and vals.get("stage_id"):
            self.filtered(
                lambda x: x.rating_active and x.rating_status == "stage"
            )._send_project_rating_mail(force_send=True)

        return result

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)

        for project in results:
            project.next_task_number_sequence_id = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "name": "Task Next Code for %s" % project.display_name,
                        "code": "project.project.next.task.code.%s" % project.id,
                        "company_id": project.company_id.id
                        if project.company_id
                        else False,
                    }
                )
            )

        return results

    def _send_project_rating_mail(self, force_send=False):
        for project in self:
            rating_template = project.stage_id.rating_mail_template_id
            if rating_template:
                project.rating_send_request(
                    rating_template, lang=project.partner_id.lang, force_send=force_send
                )

    def rating_send_request(
        self,
        template,
        lang=False,
        subtype_id=False,
        force_send=True,
        composition_mode="comment",
        notif_layout=None,
    ):
        notif_layout = "infomineo_rating_survey.mail_notification_light"
        if self.customer_recipient_id and self.customer_recipient_id.email:
            super(
                ProjectProject,
                self.with_context(
                    rating_email=self.customer_recipient_id.email,
                    rating_name=self.customer_recipient_id.name,
                ),
            ).rating_send_request(
                template,
                lang=lang,
                subtype_id=subtype_id,
                force_send=force_send,
                composition_mode=composition_mode,
                notif_layout=notif_layout,
            )

    def _get_requestor_name(self):
        self.ensure_one()
        return self.customer_recipient_id.name

    def _get_client_contact(self):
        self.ensure_one()
        return self.customer_recipient_id.email
