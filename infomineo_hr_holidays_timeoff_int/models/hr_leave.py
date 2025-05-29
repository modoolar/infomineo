from odoo import fields, models, api
import logging
import time

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # @api.model
    # def send_timeoff_remainder_action(self):
    #     _logger.info('send_timeoff_remainder_action')
    #     # Fetch pending time off requests
    #     start_time = time.time()
    #     pending_requests = self.search([('state', '=', 'confirm')])
    #     template_id = self.env.ref('infomineo_hr_holidays_timeoff_int.email_template_pending_timeoff_reminder').id
    #
    #     for request in pending_requests:
    #         # Send a reminder email to the manager for each pending request
    #         request.env['mail.template'].browse(template_id).send_mail(request.id, force_send=True)
    #     print("--- %s seconds ---" % (time.time() - start_time))

    @api.model
    def send_timeoff_remainder_action(self):
        _logger.info('Starting send_timeoff_remainder_action')
        start_time = time.time()

        # Get all pending requests with manager info
        pending_requests = self.search([('state', '=', 'confirm')])

        if not pending_requests:
            _logger.info("No pending time-off requests found")
            return

        # Group requests by manager
        manager_groups = {}
        for request in pending_requests:
            if request.employee_id.leave_manager_id:
                if request.employee_id.leave_manager_id not in manager_groups:
                    manager_groups[request.employee_id.leave_manager_id] = []
                manager_groups[request.employee_id.leave_manager_id].append(request)

        if not manager_groups:
            _logger.warning("Pending requests found but no managers assigned")
            return

        # Process each manager's requests
        for manager, requests in manager_groups.items():
            try:
                # Prepare email content
                subject = f"Reminder: {len(requests)} Pending Time-Off Requests Need Approval"

                # Create HTML table of requests
                request_lines = []
                for req in requests:
                    request_lines.append(f"""
                    <tr>
                        <td>{req.employee_id.name}</td>
                        <td>{req.holiday_status_id.name}</td>
                        <td>{req.request_date_from}</td>
                        <td>{req.request_date_to}</td>
                        <td>{req.number_of_days} days</td>
                    </tr>
                    """)

                body_html = f"""
                <p>Dear {manager.name},</p>
                <p>You have {len(requests)} pending time-off requests waiting for your approval:</p>
                <table border="1" cellpadding="5" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Employee</th>
                            <th>Leave Type</th>
                            <th>From</th>
                            <th>To</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(request_lines)}
                    </tbody>
                </table>
                <p>Please review these requests in the Odoo system.</p>
                <p>Best regards,</p>
                <p>HR Department</p>
                """

                # Send email
                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body_html,
                    'email_to': manager.work_email or manager.email,
                    'email_from': 'hrteam@infomineo.com',
                }).send()

                _logger.info(f"Sent reminder to manager {manager.name} with {len(requests)} requests")

            except Exception as e:
                _logger.error(f"Failed to send email to manager {manager.name}: {str(e)}")

        duration = time.time() - start_time
        _logger.info(f"Completed send_timeoff_remainder_action in {duration:.2f} seconds")
