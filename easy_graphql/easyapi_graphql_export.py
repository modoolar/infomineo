# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

import json
from base64 import b64encode
from odoo import models
from odoo.addons.web.controllers.main import ExportFormat, ExcelExport


class EasyapiGraphqlExport(models.AbstractModel, ExportFormat):
    _name = 'easyapi.graphql.export'
    _description = "GraphQL Export Data"

    content_type = ExcelExport.content_type
    extension = ExcelExport.extension
    from_group_data = ExcelExport.from_group_data
    from_data = ExcelExport.from_data

    def handle_graphql_export(self, values, variables):
        # Provide export input data in variable
        variable_name = values['arguments'][0]['value']['name']['value']
        variable_value = variables.get(variable_name)
        result = self.base(json.dumps(variable_value))
        alias = values['alias']
        display_key = alias['value'] if alias else values['name']['value']
        result_data = f'{{"data": {{"{display_key}": "{b64encode(result.data).decode()}"}}}}'
        result.data = result_data.encode()
        return result

