from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def send_timeoff_remainder_action(self):
        # Fetch pending time off requests
        pending_requests = self.search([('state', '=', 'confirm')])
        for request in pending_requests:
            # Generate the URL for each request
            # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # record_url = f"{base_url}/web#id={request.id}&view_type=form&model=hr.leave"
            # _logger.info(f"record_url: {record_url}")

            # Send a reminder email to the manager for each pending request
            template_id = self.env.ref('infomineo_hr_holidays_timeoff_int.email_template_pending_timeoff_reminder').id
            # request.with_context(url=record_url).env['mail.template'].browse(template_id).send_mail(request.id, force_send=True)
            request.env['mail.template'].browse(template_id).send_mail(request.id, force_send=True)
