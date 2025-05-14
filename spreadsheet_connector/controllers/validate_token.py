import re 
import ast 
import functools 
import logging 
import requests 
import json 
from odoo .exceptions import AccessError 
from odoo import http 
from odoo .addons .spreadsheet_connector .common import (invalid_response ,valid_response ,)
from odoo .http import request 
def validate_token (O000O00OO0O0O0O00 ):
    ""
    @functools .wraps (O000O00OO0O0O0O00 )
    def O0OO00O000OOOOO00 (OOOO00000OO0O0OO0 ,*O000O0OOO00OO00OO ,**O0O0O000OOOOOO000 ):
        ""
        O0O00OOOOOO000O0O =request .env ['ir.config_parameter'].sudo ()
        O0OO0OOOOO0OOO0OO =request .httprequest .headers .get ("authorization")
        if not O0OO0OOOOO0OOO0OO :
            return invalid_response ("access_token_not_found","missing access token in request header",401 ,check_json =request .__dict__ .get ('jsonrequest',None ))
        O00OOOOOOOOOO00OO =(O0O00OOOOOO000O0O .get_param ('spreadsheet_connector.sql_access_token'))
        if O00OOOOOOOOOO00OO !=O0OO0OOOOO0OOO0OO or O0OO0OOOOO0OOO0OO =='*'*40 :
            return invalid_response ("access_token","Token seems to have expired or invalid",401 ,check_json =request .__dict__ .get ('jsonrequest',None ))
        return O000O00OO0O0O0O00 (OOOO00000OO0O0OO0 ,*O000O0OOO00OO00OO ,**O0O0O000OOOOOO000 )
    return O0OO00O000OOOOO00 
