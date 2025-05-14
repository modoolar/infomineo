# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
{
    "name": "Modoolar Approvals System",
    "summary": "Specific extensions for Approvals.",
    "version": "15.0.1.10.0",
    "category": "Human Resources/Approvals",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "approvals",
        "base_tracking_o2m_fields",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/mail_activity_type_data.xml",
        "data/mail_channel_data.xml",
        "data/approvals_security_data.xml",
        "security/approval_security.xml",
        "views/advanced_approval_category_approver_views.xml",
        "views/approval_authorization_level_views.xml",
        "views/approval_category_views.xml",
        "views/approval_rule_views.xml",
        "views/approval_request_views.xml",
        "views/hr_employee_views.xml",
        "views/res_config_settings_views.xml",
        "views/ir_model_views.xml",
        "views/res_users_views.xml",
        "wizard/override_approvers_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "approvals_matrix/static/src/css/approvals_matrix.css",
        ]
    },
}
