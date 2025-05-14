# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def bi_post_init_hook(cr,registry):

    env = api.Environment(cr,SUPERUSER_ID,{})
    env['ir.config_parameter'].set_param('spreadsheet_connector.sql_access_token', '*'*40)
    

def bi_uninstall_hook(cr,registry):

    env = api.Environment(cr,SUPERUSER_ID,{})
    env['ir.config_parameter'].set_param('spreadsheet_connector.sql_access_token', '*'*40)
    