#-*- coding : utf-8 -*-

class ErrorCode:
    pass


bae_codes = ErrorCode()
svn_codes = ErrorCode()

_errors = {
    "-1"    : ("uas_err", "uas error"),
    "0"     : ("ok", "EveryThing is ok"),
    "1"     : ("unknown", "Unknown error"), 
    "2"     : ("service_unavail", "Service temporarily unavailable"),
    "3"     : ("unsupported", "Open api not supported"),
    "4"     : ("noperm", "No permission to do this operation"),
    "5"     : ("unauth_ip", "Not Authorized client ip addr"),
    "100"   : ("invalid_param", "Invalid Parameter"),
    "101"   : ("invalid_api_key", "Invalid API key"),
    "102"   : ("session_invalid", "Session key invalid or timeout"),
    "104"   : ("sign_err", "Incorrect signature"),
    "106"   : ("sign_method_err", "Unsupported singnature method"),
    "107"   : ("invalid_ts",  "Invalid timestamp"),
    "110"   : ("token_invalid", "Access Token Invalid or Timeout"),
    #bae errors
    "78000" : ("bae_ok", "EveryThing is Ok!"),
    "78001" : ("need_login", "Need login first"), 
    "78002" : ("need_mco_login", "Need login first for mobile"),
    "78003" : ("api_error", "Call API error"),
    "78005" : ("param_error", "Parameter Error"),
    "78006" : ("appid_not_bae", "This appid is not deploy to BAE"),
    "78007" : ("call_service_err", "Call thirdparty API error")
    }

svn_errors = {
     "-1"  :  ("ci_error",         "Committ Error"),
     "-2"  :  ("create_error",     "Create  Error"),
     "-3"  :  ("build_error",      "Build   Error"),
     "-4"  :  ("update_error",     "Updated Error"),
     "-5"  :  ("remove_error",     "Removed Error"),
     "-6"  :  ("done_error",       "Instance Alloc Error"),
     "0"  :   ("new",              "New"),
     "1"  :   ("ci",               "Committed"),
     "2"  :   ("create",           "Created"),
     "3"  :   ("build",            "Builded"),
     "4"  :   ("update",           "Updated"),
     "5"  :   ("remove",           "Removed"),
     "6"  :   ("done",             "Instance Allocated"),
     "101"  : ("ciing",            "Committing"),
     "102"  : ("creating",         "Creating"),
     "103"  : ("building",         "Building"),
     "104"  : ("updating",         "Updating"),
     "105"  : ("removing",         "Removing"),
     "106"  : ("d0ing",            "Allocating Instance")
}

for code, t in _errors.iteritems():
    setattr(bae_codes, t[0], code)

class BaeCliError(Exception):
    def __init__(self, messages):
        self._messages = messages

    def __str__(self):
        return self._messages

class BaeRestError(BaeCliError):
    def __init__(self, error_code, messages):
        self.error_code = str(error_code)
        self.messages   = messages

    def __str__(self):
        if _errors.has_key(self.error_code):
            detail = "Error Code {0}".format(self.error_code)
        else:
            detail = "Unknown error code {0}".format(self.error_code)

        return "{detail} -- {messages}".format(
            detail   = detail,
            messages = self.messages)

class BaeConfigError(BaeCliError):
    pass

class NotImplementError(BaeCliError):
    pass
