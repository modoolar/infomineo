# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
from odoo.tools import date_utils
from odoo.addons.excel_connector.controllers.validate_token import validate_token
from math import ceil
from urllib.parse import quote


logger = logging.getLogger(__name__)


class ExcelConnector(http.Controller):

    @validate_token
    @http.route('/excel/tablenames/', type='http', auth="none", methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def get_model_names(self, **kwargs):
        logger.info('Getting database tables')
        table_names = []
        try:
            with request.env.cr.savepoint():
                query = '''
                    SELECT 
                        relname AS table  
                    FROM 
                        pg_stat_user_tables 
                    ORDER BY relname
                '''
                request.env.cr.execute(query)
                result = request.env.cr.dictfetchall()
                for row in result:
                    table_names.append(row['table'].replace('_', '.'))
        except Exception as e:
            logger.error(str(e))
            return Response(json.dumps({'error': str(e)}, default=date_utils.json_default),
                            content_type='application/json', status=500)

        logger.info('Tables collection done')
        return Response(json.dumps(table_names, default=date_utils.json_default),
                        content_type='application/json', status=200)

    @validate_token
    @http.route(['/excel/connector/<string:model>', '/excel/connector/<string:model>/'], type='http', auth="none",
                methods=['GET', 'OPTIONS'], website=True, csrf=False, cors='*')
    def get_model_data(self, model, **kwargs):
        logger.info(f'Getting data of {model}')
        status_code = 200
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        model_size = False
        try:
            request.env.cr.execute(f'''
                SELECT
                    COUNT(*) AS size
                FROM
                    {model.replace('.', '_')}
            ''')
            model_size = request.env.cr.dictfetchall()[0]['size']
        except Exception as e:
            logger.error(str(e))
            return Response(json.dumps({'error': str(e)}, default=date_utils.json_default),
                            content_type='application/json', status=500)

        response_data = {
            "count": int(kwargs.get('count', 20000)),
            "prev": None,
            "current": int(kwargs.get('current', 1)),
            "next": None,
            "total_pages": None,
            "data": [],
            "size": model_size
        }
        response_data['total_pages'] = ceil(model_size / response_data['count'])
        response_data['next'] = None if response_data['current'] == response_data['total_pages'] or response_data[
            'total_pages'] == 0 else base_url + '/excel/connector/' + model + '?current=' + str(
            response_data['current'] + 1)
        response_data['prev'] = None if response_data[
                                            'current'] == 1 else base_url + '/excel/connector/' + model + '?current=' + str(
            response_data['current'] - 1)

        if not response_data.get('prev', False):
            response_data.pop('prev')
        if not response_data.get('next', False):
            response_data.pop('next')

        offset = (response_data['current'] - 1) * response_data['count']

        try:
            with request.env.cr.savepoint():
                query = f'''
                    SELECT *
                    FROM
                    {model.replace('.', '_')}
                    LIMIT {response_data['count']} OFFSET {offset}
                '''
                request.env.cr.execute(query)
                result = request.env.cr.dictfetchall()
                # print(result)

                response_data['data'] = result
        except Exception as e:
            logger.error(str(e))
            response_data['data'] = []
            status_code = 200

        return Response(json.dumps(response_data, default=date_utils.json_default),
                        content_type='application/json', status=status_code)

    @validate_token
    @http.route('/excel/query/data/', type='http', auth="none", methods=['GET', 'OPTIONS'], csrf=False, cors='*')
    def fetch_data(self, **kwargs):

        sql = kwargs['query']
        cursor = request.env.cr
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        cursor.execute(sql)
        data = cursor.dictfetchall()
        print(len(data))

        params = {
            "count": int(kwargs.get('count', 20000)),
            "prev": None,
            "current": int(kwargs.get('current', 1)),
            "next": None,
            "total_pages": None,
            "data": [],
            "size": len(data)
        }
        size = len(data)
        params['total_pages'] = ceil(size / params.get('count'))

        params['next'] = None if params.get('current') == params.get(
            'total_pages') or params.get(
            'total_pages') == 0 else base_url + '/excel/query/data/' + '?query=' + quote(sql) + '&current=' + str(
            params.get('current') + 1)
        params['prev'] = None if params.get(
            'current') == 1 else base_url + '/excel/query/data/' + '?query=' + quote(sql) + '&current=' + str(
            params.get('current') - 1)
        if not params.get('prev', False):
            params.pop('prev')
        if not params.get('next', False):
            params.pop('next')

        to = params.get('current') * params.get('count')
        frm = to - params.get('count')

        if not params.get('total_pages', False):
            params.pop('current')
        try:
            with http.request.env.cr.savepoint():

                values = request.env.cr.execute(f'''{sql} LIMIT {params.get('count')} OFFSET {frm} '''
                                                )

                values = request.env.cr.dictfetchall()

                params['data'] = values

        except Exception as e:
            print("except")
            # _logger.error(str(e))
            params['data'] = []
            status = 200

        return Response(json.dumps(params, default=date_utils.json_default), content_type='application/json')
