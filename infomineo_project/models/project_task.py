# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from datetime import timedelta

from email_validator import EmailNotValidError, validate_email

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

TASK_URL = "/web#id=%s&view_type=form&model=project.task&action=%s"


class ProjectTask(models.Model):
    _inherit = "project.task"

    hours_flipping = fields.Float(string="Hours Flipping/Formatting")
    hours_template_review = fields.Float()

    invoicing_office = fields.Char()
    industry_sector = fields.Char(string="Sector/Industry")

    expert_cost = fields.Float()
    client_interface_analyst = fields.Char()
    number_of_calls_delivered = fields.Integer()

    number_of_slides = fields.Integer()
    design_type = fields.Selection(
        string="Type of Design",
        selection=[
            ("basic", "Basic"),
            ("advanced", "Advanced"),
            ("creative", "Creative"),
        ],
    )

    client_contact = fields.Char(string="Requestor Email")
    requestor_name = fields.Char()
    client_charge_code = fields.Char()
    client_planned_hours = fields.Float(digits=(16, 2))
    qa_time = fields.Float(string="QA Time", digits=(16, 2))
    is_overdue = fields.Boolean(compute="_compute_task_is_overdue")

    planned_date_begin = fields.Datetime(default=fields.Datetime.now())
    planned_hours = fields.Float(string="Internal planned hours")
    date_deadline = fields.Date(string="Client Deadline")

    project_type = fields.Selection(related="project_id.project_type")
    code = fields.Char()
    current_task_number = fields.Integer()
    manager_qa_id = fields.Many2one(comodel_name="res.partner", string="Manager / QA")
    vp_representative_id = fields.Many2one(
        comodel_name="res.partner", string="VP representative"
    )

    url = fields.Char(string="URL", compute="_compute_url")
    quest_link = fields.Char()
    file_link = fields.Char(string="File ID")

    def _compute_url(self):
        action_id = self.env.ref("project.action_view_task").id
        for task in self:
            task.url = TASK_URL % (task.id, action_id)

    @api.constrains("client_contact")
    def _check_client_contact(self):
        for rec in self:
            if not rec.client_contact:
                continue

            try:
                validate_email(rec.client_contact, check_deliverability=False)
            except EmailNotValidError:
                raise ValidationError(_("Wrong format for Requestor Email address."))

    @api.constrains("user_ids", "project_id")
    def _check_assignees_required(self):
        for task in self:
            if (
                not task.user_ids
                and task.project_id.privacy_visibility == "followers"
                and task.project_id.project_type
                not in ("internal", "internal_strategic")
            ):
                raise UserError(_("Please set Assignes"))

    @api.onchange("planned_date_begin", "planned_hours", "qa_time")
    def _onchange_planned_dates(self):
        date_begin = self.planned_date_begin or fields.Date.today()
        self.planned_date_end = (
            date_begin
            + timedelta(hours=self.planned_hours)
            + timedelta(hours=self.qa_time)
        )

    @api.onchange("line_of_business")
    def _onchange_line_of_business(self):
        lob_name = "".join(
            map(
                lambda a: a[1],
                filter(
                    lambda lob: lob[0] == self.line_of_business,
                    self.fields_get(["line_of_business"])["line_of_business"][
                        "selection"
                    ],
                ),
            )
        )
        lob_abrv = "".join(map(lambda a: a[0], lob_name.split(" "))).upper()
        if self.project_id and self.project_id.name:
            self.code = "{lob}/{pn}/{ntn}".format(
                lob=lob_abrv, pn=self.project_id.name, ntn=self.current_task_number
            )
        else:
            self.code = "{lob}/{ntn}".format(lob=lob_abrv, ntn=self.current_task_number)

    @api.depends("planned_date_end", "date_deadline")
    def _compute_task_is_overdue(self):
        for rec in self:
            if rec.planned_date_end and rec.date_deadline:
                rec.is_overdue = rec.planned_date_end <= fields.Datetime.to_datetime(
                    rec.date_deadline
                )
            else:
                rec.is_overdue = False

    @api.model_create_multi
    def create(self, vals_list):
        """
        Checks whether a user has the privilege
        of creating a task on a certain project.
        """
        for vals in vals_list:
            project = self._get_project(vals)

            if project:
                self._check_task_creation_privilege(project)
                self._check_task_creation_closing_stage(project)

            if vals.get("parent_id", False) and not vals.get("line_of_business", False):
                line_of_business = (
                    self.env["project.task"]
                    .browse([vals.get("parent_id")])
                    .line_of_business
                )
                vals["line_of_business"] = line_of_business

        results = super().create(vals_list)

        for task in results:
            task.current_task_number = task.project_id.next_task_number
            task._onchange_line_of_business()
            project_sequence = self.env["ir.sequence"].search(
                [
                    (
                        "code",
                        "=",
                        "project.project.next.task.code.%s" % task.project_id.id,
                    )
                ]
            )
            if project_sequence:
                project_sequence.next_by_id()

        return results

    def _check_task_creation_privilege(self, project):
        """
        Prevent Task creation when the flag is set
        for those users which aren't Project Managers.
        """
        if project.prevent_task_creation and not self.env.user.has_group(
            "infomineo_project.group_infomineo_project_manager"
        ):
            raise UserError(
                _("Only Project Managers can create a Task on this Project.")
            )

    def _check_task_creation_closing_stage(self, project):
        """
        Prevent Task creation when state is Closing
        except for Project Administrator role.
        """
        if project.sudo().stage_id.is_closed and not self.env.user.has_group(
            "project.group_project_manager"
        ):
            raise UserError(
                _(
                    "Only Project administrator role has permission to create tasks"
                    " for projects with Closing stage"
                )
            )

    def _get_project(self, vals):
        project_id = vals.get("project_id") or self.env.context.get(
            "default_project_id"
        )
        return self.env["project.project"].browse(project_id)

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
        if self.client_contact:
            super(
                ProjectTask,
                self.with_context(
                    mail_notify_author=True,
                    rating_email=self.client_contact,
                    rating_name=self.requestor_name,
                    sudo_create_partner=True,
                ),
            ).rating_send_request(
                template,
                lang=lang,
                subtype_id=subtype_id,
                force_send=force_send,
                composition_mode=composition_mode,
                notif_layout=notif_layout,
            )
        if self.manager_qa_id and self.manager_qa_id.email:
            super(
                ProjectTask,
                self.with_context(
                    mail_notify_author=True,
                    rating_email=self.manager_qa_id.email,
                    rating_name=self.manager_qa_id.name,
                    sudo_create_partner=True,
                ),
            ).rating_send_request(
                template,
                lang=lang,
                subtype_id=subtype_id,
                force_send=force_send,
                composition_mode=composition_mode,
                notif_layout=notif_layout,
            )
        if self.vp_representative_id and self.vp_representative_id.email:
            super(
                ProjectTask,
                self.with_context(
                    mail_notify_author=True,
                    rating_email=self.vp_representative_id.email,
                    rating_name=self.vp_representative_id.name,
                    sudo_create_partner=True,
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
        return self.requestor_name

    def _get_client_contact(self):
        self.ensure_one()
        return self.client_contact

    def get_task_related_ratings(self):
        self.ensure_one()
        all_related_ratings = self.env["rating.rating"].search(
            [
                "&",
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                ("consumed", "=", True),
            ],
            order="create_date desc",
        )
        domain = [("id", "in", all_related_ratings.ids)]
        return {
            "type": "ir.actions.act_window",
            "name": _("Customer Ratings on Task"),
            "res_model": "rating.rating",
            "views": [
                [self.env.ref("project.rating_rating_view_tree_project").id, "list"],
                [False, "form"],
            ],
            "domain": domain,
            "search_view_id": [
                self.env.ref("project.rating_rating_view_search_project").id
            ],
            "target": "current",
            "context": self._context,
        }
