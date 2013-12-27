#-*- coding : utf-8 -*-

import json
import urllib
import requests
import uuid
import os
import platform

from   ..config.constants import ONEKEY_ENTRY, API_ENTRY, VERSION, PROG_NAME
from   ..errors           import *
from   ..cli.messages     import g_messager

RETRY = 3
TIMEOUT = 20
class BaeRest:
    def __init__(self, access_token, debug = False):
        self._debug = debug
        if debug:
            try:
                import urllib3
                urllib3.connectionpool.HTTPSConnection.debuglevel = 1
                urllib3.connectionpool.HTTPConnection.debuglevel  = 1
            except ImportError:
                try:
                    requests.packages.urllib3.connectionpool.HTTPSConnection.debuglevel = 1
                    requests.packages.urllib3.connectionpool.HTTPConnection.debuglevel  = 1
                except ImportError:
                    g_messager.bug("You havn't install python-requests or urllib3, debug mode will DOWN")
        self._access_token = access_token

    def _get_user_agent(self):
        try:
            plat = "%s %s" %(platform.platform(), platform.version())
        except Exception:
            plat = "unknown"

        if os.environ.has_key("BAE_LOCALENV_VERSION"):
            plat = "LOCALENV : %s" %(os.environ["BAE_LOCALENV_VERSION"])

        return 'BAE CLI %s "%s"' %(VERSION, plat)
        

    def add_token(self, data):
        if data is None or len(data) == 0:
            data = {"access_token": self._access_token}
        else:
            data["access_token"] = self._access_token
        return data

    def on_response(self, response, **kw):
        g_messager.debug(u"Server returns {0}".format(response.text))
        pass

    def post(self, path, data = None, require_code = False, require_token = True):
        if require_token:
            url_path = path + "?" + urllib.urlencode({"access_token":self._access_token})
        else:
            url_path = path
        return self._request('POST', url_path, json.dumps(data), require_code = require_code,
                             headers = {'Content-Type': 'application/json'})

    def get(self, path = '/', data = None, require_code = False, require_token = True, timeout = TIMEOUT):
        if require_token:
            data = self.add_token(data)
        if data:
            url_path = path + "?" + urllib.urlencode(data)
        else:
            url_path = path

        return self._request('GET', url_path, data = None, require_code = require_code, timeout = timeout)
    
    #Developer center not support session right now
    def _session(self):
        if not hasattr(self, "session") or not self.session:
            headers = {'Accept' : 'application/json',
                       'User-Agent' : self._get_user_agent()}
            self.session         = requests.session()
            self.session.headers = headers
            self.hooks = {
                'response' : self.on_response
                }
        return self.session

    def _request(self, method, path, data = None, require_code = False, **kw):
        def _server_error():
            g_messager.exception()
            errmsg = u"Can't understand servers infomation "
            errmsg += unicode(res.text)
            raise BaeRestError(bae_codes.api_error, errmsg)
        
        def _bae_msg(obj):
            if g_messager.use_cn and obj.has_key("error_msg"):
                return obj["error_msg"].encode("utf-8")
            elif obj.has_key("error_msg_en"):
                return obj["error_msg_en"]
            else:
                return obj["error_msg"]

        for i in range(0, RETRY):
            res = self._session().request(method, path, 
                                          data = data, hooks = self.hooks, **kw)
            try:
                obj = json.loads(res.text)

                if not require_code:
                    if not obj.has_key("error_code"):
                        return obj
                else:
                    if str(obj["error_code"]) == bae_codes.ok:
                        return obj

                if str(obj["error_code"]) == bae_codes.need_login \
                or str(obj["error_code"]) == bae_codes.need_mco_login \
                or str(obj["error_code"]) == bae_codes.token_invalid:
                    msg = "Authenticate error: {%s}\n please get a token from %s, then use '{%s} login'" %(_bae_msg(obj), ONEKEY_ENTRY, PROG_NAME)
                else:
                    msg = _bae_msg(obj)
                raise BaeRestError(obj["error_code"], msg)
            except KeyError:
                _server_error()
            except ValueError:
                _server_error()
