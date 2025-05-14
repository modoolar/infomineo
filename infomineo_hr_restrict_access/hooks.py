# Copyright (C) 2025 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging

from odoo import SUPERUSER_ID, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

HR_MODELS = [
    # "hr.employee",
    "hr.employee.category",
    # "hr.employee.public",
    "hr.department",
    "hr.job",
    "hr.plan",
    "hr.plan.activity.type",
    "hr.work.location",
    "hr.departure.reason",
    "hr.departure.wizard",
    "hr.plan.wizard",
    # "resource.resource",
]

HR_MENUS = [
    "menu_hr_root",
    "menu_hr_main",
    "menu_hr_employee_payroll",
    "menu_hr_employee",
    "hr_menu_hr_reports",
    "menu_hr_reporting_timesheet",
    "menu_human_resources_configuration",
    "menu_view_hr_job",
    "menu_human_resources_configuration_employee",
    "menu_view_employee_category_form",
    "menu_hr_department_tree",
    "menu_hr_department_kanban",
    "menu_hr_work_location_tree",
    "menu_hr_departure_reason_tree",
    "menu_config_plan",
    "menu_config_plan_types",
    "menu_config_plan_plan",
    "menu_hr_employee_user",
]


def backup_action_view(env):
    try:
        action = env.ref("hr.res_users_action_my", raise_if_not_found=False)
        if action and action.view_id:
            backup_action = action.copy()
            backup_action.name = f"INFOMINEO_HR_RESTRICT_BACKUP_{action.name}"

    except Exception as e:
        _logger.error(f"Error backing up action view: {str(e)}")
        raise


def backup_model_access(env):
    for model in HR_MODELS:
        try:
            access_rights = env["ir.model.access"].search(
                [
                    ("model_id.model", "=", model),
                ]
            )
            if access_rights:
                for access_right in access_rights:
                    access_right.write(
                        {
                            "name": f"archived_by_infomineo_hr_restrict_{access_right.name}",
                            "active": False,
                        }
                    )
        except Exception as e:
            _logger.error(f"Error backing up model access rights {model}: {str(e)}")
            raise


def modify_menu_access(env):
    hr_manager_group = env.ref("hr.group_hr_manager", raise_if_not_found=True)
    for menu_xmlid in HR_MENUS:
        try:
            menu = env.ref(f"hr.{menu_xmlid}", raise_if_not_found=False)
            if menu:
                menu.write({"groups_id": [(6, 0, [hr_manager_group.id])]})
        except Exception as e:
            _logger.error(f"Error modifying menu {menu_xmlid}: {str(e)}")
            raise


def modify_action_view(env):
    try:
        action = env.ref("hr.res_users_action_my", raise_if_not_found=False)
        if action:
            action.write({"view_id": False})
    except Exception as e:
        _logger.error(f"Error modifying action view: {str(e)}")
        raise


def modify_model_access(env):
    hr_manager_group = env.ref("hr.group_hr_manager", raise_if_not_found=True)

    for model in HR_MODELS:
        try:
            model_id = env["ir.model"].search([("model", "=", model)], limit=1)
            if not model_id:
                _logger.warning(f"Model {model} not found")
                continue

            env["ir.model.access"].create(
                {
                    "name": f'{model.replace(".", "_")}_infomineo_hr_restrict_manager',
                    "model_id": model_id.id,
                    "group_id": hr_manager_group.id,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                    "perm_unlink": True,
                }
            )
        except Exception as e:
            _logger.error(f"Error modifying access for model {model}: {str(e)}")
            raise UserError(f"Failed to modify access rights for {model}")


def backup_menu_access(env):
    for menu_xmlid in HR_MENUS:
        try:
            menu = env.ref(f"hr.{menu_xmlid}", raise_if_not_found=False)
            if not menu:
                _logger.warning(f"Menu {menu_xmlid} not found")
                continue

            groups = ",".join([str(g.id) for g in menu.groups_id])
            env.cr.execute(
                """
                INSERT INTO hr_menu_access_backup (menu_xmlid, groups)
                VALUES (%s, %s)
            """,
                (menu_xmlid, groups),
            )

        except Exception as e:
            _logger.error(f"Error backing up menu {menu_xmlid}: {str(e)}")
            raise


def restore_menu_access(env):
    try:
        env.cr.execute(
            """
            SELECT menu_xmlid, groups
            FROM hr_menu_access_backup
            WHERE menu_xmlid IS NOT NULL
        """
        )

        for menu_xmlid, groups in env.cr.fetchall():
            menu = env.ref(f"hr.{menu_xmlid}", raise_if_not_found=False)
            if not menu:
                _logger.warning(f"Menu {menu_xmlid} not found")
                continue

            group_ids = []
            if groups:
                group_ids = [int(g) for g in groups.split(",")]

            menu.write({"groups_id": [(6, 0, group_ids)]})

    except Exception as e:
        _logger.error(f"Error in restore_menu_access: {str(e)}")
        raise
    finally:
        env.cr.execute("DROP TABLE IF EXISTS hr_menu_access_backup")


def restore_action_view(env):
    try:
        action = env.ref("hr.res_users_action_my", raise_if_not_found=False)
        if action:
            backup_action = env["ir.actions.act_window"].search(
                [
                    ("name", "=", f"INFOMINEO_HR_RESTRICT_BACKUP_{action.name}"),
                ],
                limit=1,
            )

            if backup_action:
                action.write({"view_id": backup_action.view_id.id})
                backup_action.unlink()

    except Exception as e:
        _logger.error(f"Error restoring action view: {str(e)}")
        raise


def restore_model_access(env):
    for model in HR_MODELS:
        try:
            access_rights = (
                env["ir.model.access"]
                .with_context(active_test=False)
                .search(
                    [
                        ("model_id.model", "=", model),
                        ("name", "like", "archived_by_infomineo_hr_restrict_%"),
                        ("active", "=", False),
                    ]
                )
            )
            if access_rights:
                for access_right in access_rights:
                    original_name = access_right.name.replace(
                        "archived_by_infomineo_hr_restrict_", ""
                    )
                    access_right.write({"name": original_name, "active": True})

            custom_rights = env["ir.model.access"].search(
                [
                    ("model_id.model", "=", model),
                    (
                        "name",
                        "=",
                        f'{model.replace(".", "_")}_infomineo_hr_restrict_manager',
                    ),
                ]
            )
            if custom_rights:
                custom_rights.unlink()
        except Exception as e:
            _logger.error(f"Error restoring access for model {model}: {str(e)}")
            raise


def create_backup_table(cr):
    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS hr_menu_access_backup (
            id SERIAL PRIMARY KEY,
            menu_xmlid varchar,
            groups text
        )
    """
    )


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        create_backup_table(cr)
        backup_menu_access(env)
        backup_model_access(env)
        backup_action_view(env)
    except Exception as e:
        _logger.error(f"Error in pre_init_hook: {str(e)}")
        raise


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        modify_model_access(env)
        modify_menu_access(env)
        modify_action_view(env)
    except Exception as e:
        _logger.error(f"Error in post_init_hook: {str(e)}")
        raise


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        restore_model_access(env)
        restore_menu_access(env)
        restore_action_view(env)
    except Exception as e:
        _logger.error(f"Error in uninstall_hook: {str(e)}")
        raise
