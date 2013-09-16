#-*- coding: utf-8 -*-
import sys
import os

from   argparse    import ArgumentParser
from   constants   import *

class BaeBaseParser(ArgumentParser):
    def error(self, message):
        print >> sys.stderr, message
        self.print_help()
        sys.exit(-1)

class BaeParser:
    def __init__(self) :
        self._parse()

    def print_help(self):
        self.base_parser.print_help()

    def _parse(self):
        program_version_message = '%%(prog)s %s' % (VERSION)

        self.base_parser = BaeBaseParser(prog = "bae", description = LICENSE, epilog = EPILOG)
        self.base_parser.add_argument("-v", "--version", action="version", version = program_version_message)
        self.base_parser.add_argument("-D", "--debug",   action="store_true")
          
        cmd_parser      = self.base_parser.add_subparsers(dest = "cmd")
        init_parser     = cmd_parser.add_parser("login",      help = "login and init local environment")
        app_parser      = cmd_parser.add_parser("app",        help = "manage application")
        domain_parser   = cmd_parser.add_parser("domain",     help = "manage domain")
        instance_parser = cmd_parser.add_parser("instance",   help = "manage working instances")
        log_parser      = cmd_parser.add_parser("log",        help = "View   log (server, user and compile)")
        config_parser   = cmd_parser.add_parser("config",     help = "config local environment")
        service_parser  = cmd_parser.add_parser("service",    help = "Manage service")

        config_parser.add_argument("configitem", help = "Config a items in key=value pair")

        app_sub_parser = app_parser.add_subparsers(dest = "appcmd")
        app_common_parser = BaeBaseParser(add_help = False)
        app_common_parser.add_argument("-I", "--appid", 
                                       help =  "you should goto {DEVELOPER} apply a new Baidu application id, or you can use '{PROG} setupapp' to store a local cache appid".format(DEVELOPER = DEVELOPER, PROG = PROG_NAME),
                                       required = False)

        app_support_parser   = app_sub_parser.add_parser("support", help = "Get your Bae Supported languages, services", parents = [app_common_parser])
        app_setup_parser     = app_sub_parser.add_parser("setup", help = "Setup a developer app to local directory", parents = [app_common_parser])
        app_publish_parser   = app_sub_parser.add_parser("publish", help = "Publish your code")
        app_publish_parser.add_argument("--local", action = "store_true", help = "[For local environment] publish your code in local environment")	
        app_update_parser    = app_sub_parser.add_parser("update", help = "Update a Bae app by appid, if no bae id given ,it will update all bae app")
        app_update_parser.add_argument("baeappids", help = "setup a bae app with bae appid, your can use '{0} app list' get bae appid".format(PROG_NAME),
                                      nargs = "*")
        app_update_parser.add_argument("-f", "--force", action = "store_true", help = "Force update from server")
        app_create_parser    = app_sub_parser.add_parser("create", add_help = False, parents=[app_common_parser])
        app_create_parser.add_argument("-T", "--version-tool",  dest="tool", action="store",
                                   help = "Version control tools")
        app_create_parser.add_argument("-d", "--domain", action="store", help = "Domain prefix")
        app_create_parser.add_argument("-L", "--lang",   action="store",
                                   help = "Programming language you can use '{0} app status' to get more information".format(PROG_NAME))
        app_create_parser.add_argument("-t", "--type",   action="store", 
                                   help = "Bae App type, you can use '{0} app status' to get more information".format(PROG_NAME))
        app_create_parser.add_argument("appname", action = "store", help = "BAE app name")

        app_delete_parser  = app_sub_parser.add_parser("delete", help = "Delete BAE app(NOT baidu developer App)", parents=[app_common_parser])
        app_delete_parser.add_argument("-f", "--force", action = "store_true", help = "Delete app without warning")
        app_delete_parser.add_argument("baeappid", nargs = "?")

        app_list_parser    = app_sub_parser.add_parser("list",   help = "List all bae app, you can set a list of bae appid or bae appname to get certain app infos", parents = [app_common_parser])
        app_list_parser.add_argument("-v", "--detail", action = "store_true", help = "Get more detail infos")
        app_list_parser.add_argument("-l", action = "store_true", dest = "single_list", help = "List app as Single element (NOT Table format)")
        app_list_parser.add_argument("-f", "--force",  action = "store_true", help = "Force load config from server")
        app_list_parser.add_argument("baeappids", nargs = '*')

        domain_sub_parser  = domain_parser.add_subparsers(dest = "domaincmd")
        domain_base_parser = BaeBaseParser(add_help = False)
        domain_base_parser.add_argument("domain", action = "store", help = "domain name")
        domain_base_parser.add_argument("--baeappid", action = "store", help = "bae app id", required = False)
        add_parser  = domain_sub_parser.add_parser("add"   , parents = [domain_base_parser], help = "add a domain alias")
        del_parser  = domain_sub_parser.add_parser("delete", parents = [domain_base_parser], help = "delete domain alias")
        list_parser = domain_sub_parser.add_parser("list" , help = "list domain alias") 

        #Log is not supported now
        log_sub_parser    = log_parser.add_subparsers(dest = "logcmd")
        log_common_parser = BaeBaseParser(add_help = False)
        log_common_parser.add_argument("--instanceid", "-I", action = "store", help = "whinc container log do you want to view", required = True)
        log_common_parser.add_argument("--file", "-f", help = "your log file name", required = True)
        log_common_parser.add_argument("--max", "-M",   action = "store", type = int, help = "view log count, max to 1000, default 200", default = 20)
        log_common_parser.add_argument("--baeappid", action = "store", help = "set bae appid")

        log_list_parser = log_sub_parser.add_parser("list", help = "list your log files")
        log_list_parser.add_argument("--instanceid", "-s", action = "store", help = "container id (please use 'bae instance list' to get instance id)", required = True)
        log_list_parser.add_argument("--baeappid", "-I", action = "store", help = "set bae appid")
        log_sub_parser.add_parser("tail", help = "get latestest log", parents = [log_common_parser])
        log_sub_parser.add_parser("head", help = "get oledest log", parents = [log_common_parser])

        service_sub_parser       = service_parser.add_subparsers(dest = "servicecmd")
        service_list_parser      = service_sub_parser.add_parser("list",   help    = "list BAE supported services")
        service_status_parser    = service_sub_parser.add_parser("status", help    = "list all service of your application")
        service_apply_parser     = service_sub_parser.add_parser("create", help    = "apply a service flavor")
        service_apply_parser.add_argument("-t", "--type",action = "store", help = "set your service flavor type")

        instance_sub_parser      = instance_parser.add_subparsers(dest = "instancecmd")
        instance_common_parser   = BaeBaseParser(add_help = False)
        instance_common_parser.add_argument("--baeappid", action = "store", required=False)
        instance_list_parser     = instance_sub_parser.add_parser("list", help = "List all your instance", parents=[instance_common_parser])
        instance_list_parser.add_argument("insids", nargs = "*")
        instance_scale_parser    = instance_sub_parser.add_parser("scale", help = "Scale your instance", parents = [instance_common_parser])
        instance_scale_parser.add_argument("scalenum", type=int, action="store")
        instance_restart_parser  = instance_sub_parser.add_parser("restart", help = "Restart a instance", parents = [instance_common_parser])
        instance_restart_parser.add_argument("--local", action = "store_true", help = "[For local environment] restart local web server")
        instance_restart_parser.add_argument("insids",  nargs = "*",action = "store")
        instance_start_parser  = instance_sub_parser.add_parser("start", help = "Start a instance", parents = [instance_common_parser])
        instance_start_parser.add_argument("--local", action = "store_true", help = "[For local environment] Start local web server")
        instance_stop_parser  = instance_sub_parser.add_parser("stop", help = "Stop a instance", parents = [instance_common_parser])
        instance_stop_parser.add_argument("--local", action = "store_true", help = "[For local environment] Stop local web server")

        self.args = self.base_parser.parse_args()
    
    def __getattr__(self, name):
        if hasattr(self.args, name):
            return getattr(self.args, name)
        else:
            return None
