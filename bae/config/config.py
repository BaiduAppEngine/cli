#-*- coding : utf-8 -*-
import os
import traceback
import yaml
import prettytable
import json

from   .constants      import BAE_GLOBAL_CONFIG, BAE_APP_CONFIG, DEV_APP_CONFIG
from   ..errors        import BaeConfigError, svn_errors
from   ..cli.messages  import g_messager

class AttrDict:
    def __init__(self, config, expect_keys):
        if config is None:
            #just a model
            for expect_key, clz, required in expect_keys:
                self.__dict__[expect_key] = clz()
        else:
            for expect_key, clz, required in expect_keys:
                if config.has_key(expect_key):
                    if  isinstance(config[expect_key], list):
                        self.__dict__[expect_key] = []
                        for elem in config[expect_key]:
                            self.__dict__[expect_key].append(clz(elem))
                    else:
                        self.__dict__[expect_key]      = clz(config[expect_key])
                else:
                    if required:
                        raise BaeConfigError("config : {0}  not exists".format(expect_key))
                    else:
                        self.__dict__[expect_key] = None

        self._expect_keys = expect_keys

    def configs(self):
        config = {}
        for expect_key, clz, required in self._expect_keys:
            if self.__dict__.has_key(expect_key) and self.__dict__[expect_key] is not None:
                if isinstance(self.__dict__[expect_key],list):
                    config[expect_key] = []
                    for elem in self.__dict__[expect_key]:
                        if isinstance(elem, str) or isinstance(elem, bool):
                            config[expect_key].append(elem)
                        else:
                            config[expect_key].append(elem.configs())
                elif clz.__name__ == "str" or clz.__name__ == "bool":
                    config[expect_key] = self.__dict__[expect_key]
                else:
                    config[expect_key] = self.__dict__[expect_key].configs()
        return config
    
class DevUser(AttrDict):
    _expect_keys = (
        ("cipher",    str,  False), 
        ("name",      str,  False)
        )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, DevUser._expect_keys)

    def __str__(self):
        return '''User Infomations:
User name:{0}'''.format(self.name)
        return ""

class BaeInfo(AttrDict):
    _expect_keys = (
        ("max_app_num",  str, True),
        ("cur_app_num",  str, True),
        ("cidWorkerNum", str, True),
        ("cidWebappNum", str, True)
        )
    def __init__(self, config = None):
        AttrDict.__init__(self, config, BaeInfo._expect_keys)

    def __str__(self):
        return '''Your Baidu App Infos
Max  App    Number     : {0}
Cur  App    Number     : {1}
Cur  Web    Apps Number: {2}
Cur  Worker AppsNumber : {3}'''.format(
            str(self.max_app_num), 
            str(self.cur_app_num), 
            str(self.cidWorkerNum), 
            str(self.cidWebappNum))

class BaeSupport(AttrDict):
    _expect_keys = (
        ("lang_types",    str,  True),
        ("createtypes",   str,  True),
        ("version_tools", str,  True)
        )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, BaeSupport._expect_keys)

    def __str__(self):
        return '''supported language      : {0} 
supported runtime Types : {1}
code Version Tools      : {2}'''.format(
            ", ".join(self.lang_types), 
            ", ".join(self.createtypes),
            ", ".join(self.version_tools)
            )

class BaeGlobals(AttrDict):
    _expect_keys = (
        ("user",      DevUser, True), 
        ("use_color",     bool, False),
        ("api_entry",     str, False),
        ('use_cn',        bool, False)
        )

    def __init__(self, config  = None):
        AttrDict.__init__(self, config, BaeGlobals._expect_keys)

    def __str__(self):
        return '''Global Configs : 
{0}'''.format(str(self.user))


class DomainAlias(AttrDict):
    _expect_keys = (
        ("alias_domain", str, True),
        ("cdatetime",    str, False),
        )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, DomainAlias._expect_keys)

    def __str__(self):
        return self.alias_domain

class BaeApp(AttrDict):
    _expect_keys = (
        ("domain"            ,str,  False),
        ("createtype"        ,str,  True),
        ("lang_type"         ,str,  True),
        ("version_type"      ,str,  False),
        ("repos_url"         ,str,  False),
        ("release_revision"  ,str,  False),
        ("appid"             ,str,  True),
        ('appname'           ,str,  False),
        ('name'              ,str,  True),
        ('cdatetime'         ,str,  True),
        ("status"            ,str,  True),
        ('inum'              ,str,  False),
        ("alias"             ,DomainAlias, True)
        )
    def __init__(self, config = None):
        AttrDict.__init__(self, config, BaeApp._expect_keys)

    def tuple(self):
        datestr, statusstr = self._get_str()
        return (self.appid, self.name, self.lang_type, self.domain ,datestr, self.repos_url, 
                self.createtype, self.version_type, self.release_revision[0:8], 
                ";".join([str(x) for x in self.alias]), statusstr, self.inum)

    def _get_str(self):
        try:
            import time
            datestr = time.strftime("%Y/%b/%d %H:%M:%S", time.localtime(float(self.cdatetime)))
        except IOError:
            datestr = None

        if svn_errors.has_key(str(self.status)):
            statusstr = svn_errors[str(self.status)][1]
        else:
            statusstr =  "Unknown"

        if int(self.status) < 0:
            statusstr = g_messager.redstr(statusstr)
        elif int(self.status) < 100:
            statusstr = g_messager.greenstr(statusstr)
        else:
            statusstr  = g_messager.yellowstr(statusstr)

        return (datestr, statusstr)

    def __str__(self):
        datestr, statusstr = self._get_str()
        return'''--------------------------
BAE app {0} {1}: 
description     : {2}
pro language    : {3}
domain          : {4}
created  at     : {5}
code repos url  : {6}
runtime Type    : {7}
code tool       : {8}
code revision   : {9}
Domain Alias    : {10}
status          : {11}
--------------------------'''.format(
            self.appid,
            self.name,
            self.appname,
            self.lang_type, 
            self.domain, 
            datestr, 
            self.repos_url, 
            self.createtype,
            self.version_type,
            self.release_revision,
            "\n".join([str(x) for x in self.alias]),
            statusstr)


class DevApp(AttrDict):
    _expect_keys = (
        ("app_id",   str,    True),
        ("support",BaeSupport, False)
       )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, DevApp._expect_keys)

class BaeInstanceGroup(AttrDict):
    _expect_keys = (
        ("gid",          str, True),
        ('name',         str, True),
        ('lang',         str, True),
        ('type',         str, True),
        ('userid',       str, True),
        ('inum',         int, True),
        ('checktime',    str, True),
        ('checknum',     int, True),
        ('status',       str, True)
        )

    _status = {
        'new'         :  0,
        'running'     :  1,
        'deploying'   :  0,
        'deployfail'  : -1,
        'checking'    :  0,
        'checkfail'   : -1, 
        'restarting'  :  0,
        'restartfail' : -1
        }

    def __init__(self, config = None):
        AttrDict.__init__(self, config, BaeInstanceGroup._expect_keys)

    def __str__(self):
        return '''group ID {0} infomation :
group name:      {1}
language type:   {2}
group type:      {3}
user  ID :       {4}
instance count:  {5}
status:          {6}
'''.format(self.gid, self.name, self.lang, self.type, self.userid, self.inum, _instance_status_str(BaeInstanceGroup._status, self.status))


class ServicePackage(AttrDict):
    _expect_keys = (
        #("type_name",       str, True), ###comments by pysqz
        #("type_detail",     str, True), ###comments by pysqz
        ("type_name",       str, False),
        ("type_detail",     str, False),
        )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, ServicePackage._expect_keys)
    
    def __str__(self):
        return "{0} : {1}".format(self.type_name, self.type_detail)

class Resource(AttrDict):
    _expect_keys = (
        ("resource_name",   str, True),
        ("service_name",    str, True),
        ("service_type",    str, True),
        #("service_package", ServicePackage, True), ###comments by pysqz
        ("base_info",       dict, True),
        )

    def __init__(self, config = None):
        AttrDict.__init__(self, config, Resource._expect_keys)

    def tuple(self):
        base_info  = "\n".join(["{0}:{1}".format(k,v) for k, v in self.base_info.iteritems()])
        #return (self.resource_name, self.resource_name, self.service_name, self.service_package.type_name, base_info) ###comments by pysqz
        return (self.resource_name, self.service_name, self.service_name, "N/A", base_info)
        
    
class Service(AttrDict):
    _expect_keys = (
        ("service_name",    str, True),
        ("display_name",    str, True),
        #("provider",       str, True),
        #("service_package", ServicePackage, True), ###comments by pysqz
        ("service_package", ServicePackage, False),
        )
    
    def __init__(self, config = None):
        AttrDict.__init__(self, config, Service._expect_keys)

    def __str__(self):
        return self.service_name

    def tuple(self):
        #return (self.service_name, self.display_name, "".join([x.type_name for x in self.service_package])) ###comments by pysqz
        return (self.service_name, self.display_name, "N/A")

class BaeInstance(AttrDict):
    _expect_keys = (
        ("fid",          str, True),
        ("displayname",  str, True),
        ("status",       str, True),
        )

    _status = {
        'blank'       :  0,
        'creating'    :  0,
        'createfail'  : -1,
        'running'     :  1,
        'deploying'   :  0,
        'deployfail'  : -1,
        'deleting'    :  0,
        'deletefail'  : -1,
        'restarting'  :  0,
        'restartfail' : -1
        }

    def __init__(self, config = None):
        AttrDict.__init__(self, config, BaeInstance._expect_keys)

    def tuple(self):
        return (self.fid, self.displayname, _instance_status_str(BaeInstance._status, self.status))

    def __str__(self):
        return '''----------------------------
instance ID : {0}
name        : {1}
display name: {2}
host        : {3}
webport     : {4}
SSHPort     : {5}
status      : {6}
-----------------------------'''.format(
            self.fid,
            self.name,
            self.displayname,
            self.host,
            self.webport,
            self.sshport,
            _instance_status_str(BaeInstance._status, self.status)
            )

class BaeConfigFile:
    def __init__(self, path):
        self.confpath = path

    def load(self):
        config  = yaml.load(open(self.confpath, "r"))
        self._loadenv() #env varaible overrides config files
        
        return config

    #TODO support BAE environment
    def _loadenv(self):
        pass

    def save(self, config):
        yaml.dump(config, stream = open(self.confpath, "w"), default_flow_style=False)

        #0600 is relative safe
        os.chmod(self.confpath, 0600)

    def exists(self):
        return os.path.exists(self.confpath)

    def dirname(self):
        if self.confpath:
            return os.path.dirname(self.confpath)
        else:
            raise IOError("confpath not found")

class BaeGlobalConfig:
    def __init__(self):
        home_dir  = os.path.expanduser("~")
        path      = os.path.join(home_dir, BAE_GLOBAL_CONFIG)
        
        self._configfile = BaeConfigFile(path)

        self.model = BaeGlobals()

    #reload configs
    def load(self):
        _config = self._configfile.load()
        self.model = BaeGlobals(_config)

    def save(self):
        self._configfile.save(self.model.configs())

class DevAppConfig: 
    def __init__(self, path = None):
        if not path:
            cur_dir = os.getcwd()
            home_dir = os.path.expanduser("~")
        
            while cur_dir != home_dir and cur_dir != '/':
                tmppath = os.path.join(cur_dir, DEV_APP_CONFIG)
                if os.path.exists(tmppath):
                    path = tmppath
                    break
                #search parent
                cur_dir = os.path.realpath(os.path.join(cur_dir, os.pardir))

            if cur_dir == home_dir or cur_dir == '/':
                #search in home dir
                tmppath = os.path.join(cur_dir, DEV_APP_CONFIG)
                if os.path.exists(tmppath):
                    path = tmppath
                else:
                    raise IOError("Can't find bae app config file")

        self._configfile = BaeConfigFile(path)
            
        if os.path.exists(path):
            _config    = self._configfile.load()
            self.model = DevApp(_config)
        else:
            self.model = DevApp()
        
    def load_bae_app(self):
        self.bae_app_configs = []
        
        self.cur_bae_app     = None

        path = self.appdir()
        for subdir in os.listdir(path):
            cur_dir    = os.path.join(path, subdir)
            bae_config = os.path.join(cur_dir, BAE_APP_CONFIG)
            
            if os.path.isdir(cur_dir) and os.path.exists(bae_config):
                bae_app_conf = BaeAppConfig(bae_config)
                bae_app_conf.load()
                self.bae_app_configs.append(bae_app_conf)
                if os.getcwd().startswith(os.path.normpath(cur_dir)):
                    self.cur_bae_app = bae_app_conf

    def appdir(self):
        return self._configfile.dirname()

    def load(self):
        _config = self._configfile.load()
        self.model = DevApp(_config)
        self.load_bae_app()

    def save(self):
        self._configfile.save(self.model.configs())
        
        for bae_app_config in self.bae_app_configs:
            bae_app_config.save()

class BaeAppConfig:
    def __init__(self, path = None):
        self._configfile = BaeConfigFile(path)

    def load(self):
        if self._configfile.exists():
            _config = self._configfile.load()
            self.model = BaeApp(_config)
        else:
            self.model = BaeApp()
    def save(self):
        return self._configfile.save(self.model.configs())

    def dirname(self):
        return self._configfile.dirname()



def _format_table(title, headers, rows):
    print g_messager.magentastr(title)
    table = prettytable.PrettyTable(headers)
    table.padding_width = 1
    for row in rows:
        table.add_row(row)
    return table

def _instance_status_str(status_dict, key):
    if not status_dict.has_key(key):
        status = -1
        key    = "Unknown"
    else:
        status = status_dict[key]
        
    if status == -1:
        return g_messager.redstr(key)
    elif status == 1:
        return g_messager.greenstr(key)
    else:
        return g_messager.yellowstr(key)
    
_BAE_APP_HEADER   = map(lambda x: g_messager.magentastr(x), ("appid", 'appname','language type','domain','created at','code repos URL', 'runtime type', 'code tool', 'revision', 'domain alias', 'status', 'instance count'))
_INSTANCE_HEADER  = map(lambda x: g_messager.magentastr(x), ('instance ID','display name', 'status'))
_SERVICE_HEADER   = map(lambda x: g_messager.magentastr(x), ('index', 'service name', 'name' , 'flavor'))
_RESOURCE_HEADER  = map(lambda x: g_messager.magentastr(x), ('index', "resource name", 'service name', 'name' , 'flavor', 'service infomation'))

def bae_app_detail_table(title, rows):
    return  _format_table(title, _BAE_APP_HEADER, rows).get_string(sortby = _BAE_APP_HEADER[4],
                                                              reversesort = True)
def bae_app_table(title, rows):
    return _format_table(title, _BAE_APP_HEADER, rows).get_string(fields = list(_BAE_APP_HEADER[i] for i in [0, 1, 2, 5, 11]))

def instance_table(title, rows):
    return _format_table(title, _INSTANCE_HEADER, rows)

def service_table(title, rows):
    return _format_table(title, _SERVICE_HEADER,  rows)

def resource_table(title, rows):
    tb =  _format_table(title, _RESOURCE_HEADER, rows)
    #tb[5].align = "l"
    return tb
