# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from .substitutions.rating_mixin import patch_rating_mixin_methods


def are_we_in_test_mode():
    from odoo.tools import config

    return config.get("test_enable") or config.get("test_file")


def post_init_hook(cr, registry):
    if are_we_in_test_mode():
        cr.execute(
            """
            update ir_model_access
            set perm_unlink = true
            where id in (
                select res_id from ir_model_data
                where model = 'ir.model.access'
                and name = 'access_project_task'
                and module = 'project'
            );
            """
        )
        cr.execute(
            """SELECT arch_db FROM ir_ui_view
            WHERE name = 'project.view.task.form2'
            AND arch_fs ILIKE 'infomineo_project%'
            """
        )
        arch_db = cr.fetchone()[0]
        arch_db = arch_db.replace(
            "<attribute name=\"attrs\">{'readonly': "
            "[('project_id', '!=', False)]}</attribute>",
            "",
        )
        arch_db = arch_db.replace("'", "&quot;")

        update_quary = """
                    UPDATE ir_ui_view
                    SET arch_db = %(view_body)s
                    WHERE name = 'project.view.task.form2'
                    AND arch_fs ILIKE 'infomineo_project%%'
                    """
        cr.execute(update_quary, {"view_body": arch_db})


def post_load():
    patch_rating_mixin_methods()
