import json 
import logging 
import datetime
import sys
from odoo import http 
from odoo .http import request ,Response 
from itertools import groupby 
from odoo .tools import date_utils 
from odoo .addons .spreadsheet_connector .controllers .validate_token import validate_token 
from math import ceil
logger = logging.getLogger(__name__)


class SqlConnector (http .Controller ):
    ""

    @http.route('/sql/tablenames/', type='http', auth="none", methods=['GET', 'OPTIONS'], csrf=False, cors='*')
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
    @http.route(['/sql/connector/<string:model>', '/sql/connector/<string:model>/'], type='http', auth="none",
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
            'total_pages'] == 0 else base_url + '/sql/connector/' + model + '?current=' + str(
            response_data['current'] + 1)
        response_data['prev'] = None if response_data[
                                            'current'] == 1 else base_url + '/sql/connector/' + model + '?current=' + str(
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
                for row in result:
                    for key, value in row.items():

                        if isinstance(value, dict):
                            row[key] = list(value.values())[0]

                        if isinstance(value, datetime.datetime):
                            row[key] = value.strftime("%Y%m%d%H%M%S")
                        elif isinstance(value, datetime.date):
                            row[key] = value.strftime("%Y%m%d")
                response_data['data'] = result
        except Exception as e:
            logger.error(str(e))
            response_data['data'] = []
            status_code = 200

        data = self.size_data(response_data)
        return Response(json.dumps(data, default=date_utils.json_default),
                        content_type='application/json', status=status_code)

    def size_data(self, response):
        try:
            data = response

            # Access the nested list of dictionaries
            if "data" in data and isinstance(data["data"], list):
                column_sizes = {}
                for row in data["data"]:
                    for key, value in row.items():
                        value_size = sys.getsizeof(value)
                        if key in column_sizes:
                            column_sizes[key] += value_size
                        else:
                            column_sizes[key] = value_size

                # Print the size of each column in megabytes
                # print("Column sizes in megabytes (MB):")
                # for column, size in column_sizes.items():
                #     print(f"{column}: {size / (1024 * 1024):.6f} MB")

                # Check if any column is larger than 10 MB and set its values to null
                columns_to_nullify = [column for column, size in column_sizes.items() if
                                      size > 10 * 1024 * 1024]  # 10 MB

                if columns_to_nullify:
                    print("\nColumns greater than 10 MB will be nullified.")
                    for row in data["data"]:
                        for column in columns_to_nullify:
                            row[column] = None

                # Find the largest column
                largest_column = max(column_sizes, key=column_sizes.get)
                largest_size = column_sizes[largest_column] / (1024 * 1024)  # Convert to MB
                return data
                # print(f"\nThe largest column is '{largest_column}' with a size of {largest_size:.6f} MB")

            else:
                print("Expected 'data' to be a list of dictionaries.")

        except Exception as e:
            print(f"An error occurred: {e}")
