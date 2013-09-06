#-*- coding : utf-8 -*-

import os
from   ..errors           import *
from   ..config.constants import BAE_APP_CONFIG
from   .messages         import g_messager
SVN = "svn"
GIT = "git"


def get_tool(name, repos, localdir):
    if name == "svn":
        return SvnTool(repos, localdir)
    elif name == "git":
        return GitTool(repos, localdir)
    else:
        raise NotImplementError(name  + " tool case not exist")

class SvnTool:
    def __init__(self, repos, localdir):
        self._repos    = repos
        self._localdir = localdir

    def run(self, cmd):
        g_messager.debug(cmd)
        os.system(cmd)

    def pull(self):
        if not os.path.exists(os.path.join(self._localdir, ".svn")):
            svncmd = "{0} co {1} {2}".format(SVN, self._repos, self._localdir)
        else:
            svncmd = "{0} up {1}".format(SVN, self._localdir)
        self.run(svncmd)
 
    def add(self):
        svncmd = "{0} ps svn:ignore {1} {2}".format(SVN, BAE_APP_CONFIG, self._localdir)
        self.run(svncmd)
        svncmd = "{0} add {1}/* --force".format(SVN, self._localdir)
        self.run(svncmd)

    def push(self):
        self.add()
        svncmd = "{0} ci {1} -m 'Bae Client automate'".format(SVN, self._localdir)
        self.run(svncmd)
        

class GitTool:
    def __init__(self, repos, localdir):
        self._repos    = repos
        self._localdir = localdir

    def run(self, cmd):
        g_messager.debug(cmd)
        os.system(cmd)

    def pull(self):
        c = os.getcwd()
        if not os.path.exists(os.path.join(self._localdir, ".git")):
            #FIXME BUG#3358 zhou
            gitcmd = "cd {2};{0} init;{0} remote add origin {1};{0} fetch;{0} branch master origin/master;{0} checkout master;cd {3}".format(GIT, self._repos, self._localdir, c)
            #gitcmd = "{0} clone {1} {2};cd {3}".format(GIT, self._repos, self._localdir, c)
        else:
            gitcmd = "cd {1};{0} pull;cd {2} ".format(GIT, self._localdir, c)

        self.run(gitcmd)
        
    def push(self):
        c = os.getcwd()
        os.system("touch {0}/.gitignore".format(self._localdir))
        os.system("cat '.baeapp' > {0}/.gitignore".format(self._localdir))
        gitcmd = "{0} commit -m 'Bae Client autoamte' {1}".format(GIT, self._localdir)
        self.run(gitcmd)
        gitcmd = "cd {1};{0} push origin master; cd {2}".format(GIT, self._localdir, c)
        self.run(gitcmd)

        
