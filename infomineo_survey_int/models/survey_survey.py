from email.policy import default

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class Survey (models.Model):
    _inherit = 'survey.survey'

    survey_type = fields.Selection([('onboarding', 'Onboarding')], 'Survey Type')
    share_type = fields.Selection([('auto', 'Automatic'), ('manual', 'Manual')], 'Share Type', default='manual')

    @api.model
    def auto_send_survey_action(self):
        _logger.info('auto_send_survey_action')
        auto_survey_ids = self.search([('share_type', '=', 'auto')])
        if auto_survey_ids:
            for auto_survey in auto_survey_ids:
                if auto_survey.survey_type == 'onboarding':
                    answered_partners_ids = auto_survey.user_input_ids.mapped('partner_id')
                    yesterday = date.today() - timedelta(days=1)
                    new_partners_ids = self.env['res.users'].search([
                        ('create_date', '>=', yesterday.strftime('%Y-%m-%d 00:00:00')),
                        ('create_date', '<=', yesterday.strftime('%Y-%m-%d 23:59:59'))
                    ]).mapped('partner_id')

                    not_answered_new_partner_ids = list(set(new_partners_ids.ids) - set(answered_partners_ids.ids))
                    if not_answered_new_partner_ids:
                        template = self.env.ref('survey.mail_template_user_input_invite', raise_if_not_found=False)
                        local_context = dict(
                            default_survey_id=auto_survey.id,
                            default_use_template=bool(template),
                            default_template_id=template and template.id or False,
                            notif_layout='mail.mail_notification_light',
                        )
                        survey_share_wizard = self.env['survey.invite'].with_user(auto_survey.user_id.id).with_context(local_context).sudo().create({'survey_id': auto_survey.id,
                                                          'partner_ids': not_answered_new_partner_ids,
                                                          })
                        if survey_share_wizard:
                            survey_share_wizard.action_invite()

    def send_non_respondents_list_to_responsible(self):
        mail_mail = self.env['mail.mail']

        for survey in self:
            if not survey.user_id or not survey.user_id.email:
                continue  # Skip if no responsible person set

            # Get all employees who haven't completed the survey using partner table
            yesterday = date.today() - timedelta(days=1)
            two_weeks_ago = date.today() - timedelta(days=14)
            # new users for two weeks exclude who joined yesterday
            all_partners = self.env['res.users'].search([
                        ('create_date', '>=', two_weeks_ago.strftime('%Y-%m-%d 00:00:00')),
                        ('create_date', '<=', yesterday.strftime('%Y-%m-%d 00:00:00'))
                    ]).mapped('partner_id')

            # Get employees who have already answered
            responses = self.env['survey.user_input'].search([
                ('survey_id', '=', survey.id),
                ('state', '=', 'done')
            ])
            respondent_partner_ids = responses.mapped('partner_id')

            # Find employees who haven't responded
            non_respondents = all_partners.filtered(
                lambda p: p not in respondent_partner_ids
            )

            non_respondents_ids = self.env['res.partner'].browse(non_respondents)

            if not non_respondents:
                continue  # Skip if everyone has responded

            # Prepare the list of non-respondents
            partners_list = "\n".join([
                f"<li>{partner.name}</li>"
                for partner in non_respondents
            ])

            email_values = {
                'subject': _("Survey Reminder: List of Employees Pending Response - %s") % survey.title,
                'body_html': _("""
                    <p>Hello %s,</p>
                    <p>Here is the list of employees who haven't yet completed the survey <strong>%s</strong>:</p>
                    <ul>
                        %s
                    </ul>
                    <p>Total pending: %d employees</p>
                    <p>The survey can be accessed here: <a  t-attf-href="/web?#id=%s&amp;view_type=form&amp;model=survey.survey">%s</a></p>
                    <p>Please follow up with these employees as needed.</p>
                    <p>Thank you!</p>
                """) % (
                    survey.user_id.name,
                    survey.title,
                    partners_list,
                    len(non_respondents),
                    survey.id,
                    survey.title
                ),
                'email_to': survey.user_id.email,
                'email_from': self.env.user.email or self.env.company.email,
            }

            mail = mail_mail.with_user(survey.user_id.id).create(email_values)
            mail.send()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': _("Reminder list sent to survey responsible"),
                'type': 'rainbow_man',
            }
        }

    @api.model
    def auto_send_survey_remainder_action(self):
        _logger.info('auto_send_survey_remainder_action')
        auto_survey_ids = self.search([('share_type', '=', 'auto')])
        if auto_survey_ids:
            for auto_survey in auto_survey_ids:
                if auto_survey.survey_type == 'onboarding':
                    yesterday = date.today() - timedelta(days=1)
                    all_partners_ids = self.env['res.users'].search([
                        ('create_date', '<=', yesterday.strftime('%Y-%m-%d 00:00:00'))
                    ]).mapped('partner_id')
                    answered_partners_ids = auto_survey.user_input_ids.filtered(lambda e:e.state in ['done']).mapped('partner_id')

                    not_answered_partners_ids = list(set(all_partners_ids.ids) - set(answered_partners_ids.ids))
                    # not_answered_partners_ids = (auto_survey.user_input_ids
                    #                          .filtered(lambda e:e.state in ['new', 'in_progress'])
                    #                          .mapped('partner_id'))

                    if not_answered_partners_ids:
                        template = self.env.ref('survey.mail_template_user_input_invite', raise_if_not_found=False)
                        local_context = dict(
                            default_survey_id=auto_survey.id,
                            default_use_template=bool(template),
                            default_template_id=template and template.id or False,
                            notif_layout='mail.mail_notification_light',
                        )
                        remainder_survey_share_wizard = self.env['survey.invite'].with_user(auto_survey.user_id.id).with_context(local_context).sudo().create({'survey_id': auto_survey.id,
                                                          'partner_ids': not_answered_partners_ids,
                                                          })
                        remainder_survey_share_wizard.update({'subject': 'Remainder to ' + remainder_survey_share_wizard.subject})
                        if remainder_survey_share_wizard:
                            auto_survey.send_non_respondents_list_to_responsible()
                            remainder_survey_share_wizard.action_invite()

