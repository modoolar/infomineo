import hashlib #line:2
import logging #line:3
import os #line:4
import requests #line:5
from odoo import models ,fields ,api ,_ #line:6

class SqlWebConnectorSetting (models .TransientModel ):#line:12
    ""#line:13
    _inherit ='res.config.settings'#line:15
    def _get_sql_url (OOO0000000OO000OO ):#line:19
        OO00OOOO0OOOO0000 =OOO0000000OO000OO .env ['ir.config_parameter'].sudo ().get_param ('web.base.url')#line:20
        OOO0000000OO000OO .env ['ir.config_parameter'].set_param ('spreadsheet_connector.sql_url',OO00OOOO0OOOO0000 )#line:21
        return OO00OOOO0OOOO0000 #line:22
    sql_url =fields .Char (string ='Connector Url',default =_get_sql_url ,readonly =True )#line:24
    sql_access_token =fields .Char (string ='Access Token',default =(' '*40 ))#line:25
    def set_values (O0OO0OO00OOOOO0O0 ):#line:27
        O0OO00000OO0O0000 =super (SqlWebConnectorSetting ,O0OO0OO00OOOOO0O0 ).set_values ()#line:28
        O0OO0OO00OOOOO0O0 .env ['ir.config_parameter'].set_param ('spreadsheet_connector.sql_url',O0OO0OO00OOOOO0O0 .sql_url )#line:29
        O0OO0OO00OOOOO0O0 .env ['ir.config_parameter'].set_param ('spreadsheet_connector.sql_access_token',O0OO0OO00OOOOO0O0 .sql_access_token )#line:30
        return O0OO00000OO0O0000 #line:33
    @api .model #line:35
    def get_values (O00OO00OO0OO00OOO ):#line:36
        O0OOOOOO0O0000OO0 =super (SqlWebConnectorSetting ,O00OO00OO0OO00OOO ).get_values ()#line:38
        OO00OOOOOOOOO000O =O00OO00OO0OO00OOO .env ['ir.config_parameter'].sudo ()#line:39
        OOOOOOO0O000O000O =OO00OOOOOOOOO000O .get_param ('spreadsheet_connector.sql_access_token')#line:40
        O00O00O0OO0000000 =OO00OOOOOOOOO000O .get_param ('spreadsheet_connector.sql_url')#line:41
        O0OOOOOO0O0000OO0 .update (sql_access_token =OOOOOOO0O000O000O ,sql_url =O00O00O0OO0000000 ,)#line:45
        return O0OOOOOO0O0000OO0 #line:47
    def nonce (OOOO0O0O00O0000OO ,length =40 ,prefix =""):#line:49
        O000O00O0O0O0000O =os .urandom (length )#line:50
        return "{}_{}".format (prefix ,str (hashlib .sha1 (O000O00O0O0O0000O ).hexdigest ()))#line:51
    def sql_generate_token (OOO00OO0O0O0OOOO0 ):#line:53
        OOO00OO0O0O0OOOO0 .env ['ir.config_parameter'].set_param ('spreadsheet_connector.sql_access_token',OOO00OO0O0O0OOOO0 .nonce ())#line:55
