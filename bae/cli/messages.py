#-*- coding : utf-8 -*-

'''
colored message.
https://pypi.python.org/pypi/colorama
'''

import colorama
import getpass
import traceback
import sys

try:
    import readline
except ImportError:
    pass

from   ..config.constants import BAE_SUPPORT

colorama.init()
NORMAL    = 0
INPUT     = 1
YES_OR_NO = 2
PASSWORD  = 3
SELECT    = 4
OUTPUT    = 5

DEBUG     = False

class BaeMessage:
    def __init__(self, use_color = True, use_cn = False):
        self.use_color = use_color
        self.use_cn    = use_cn

    def colorstr(self, message, color):
        if self.use_color:
            return u"{color}{message}{reset}".format(
                color   = color, 
                message = message, 
                reset   = colorama.Style.RESET_ALL)
        else:
            return message

    def redstr(self, message):
        return self.colorstr(message, colorama.Fore.RED)

    def magentastr(self, message):
        return self.colorstr(message, colorama.Fore.MAGENTA)

    def greenstr(self, message):
        return self.colorstr(message, colorama.Fore.GREEN)

    def yellowstr(self, message):
        return self.colorstr(message, colorama.Fore.YELLOW)

    def _print(self, message, color = None, type = NORMAL, *args):
        #message = message.decode("utf-8")
        if type == NORMAL:
            msgs = message.splitlines()
            print "\n".join(self.colorstr("<<  ", color) + msg for msg in msgs) 

        if type == OUTPUT:
            
            msgs = message.splitlines()
            print "\n".join(msg for msg in msgs) 

        if type == INPUT:
            msg = self.colorstr("{0} >> ".format(message), color)
            return raw_input(msg)

        if type == YES_OR_NO:
            msg = self.colorstr("{0} >> ".format(message), color)
            answer = raw_input(msg)

            while True:
                if answer and len(answer) == 1 and answer.upper() == "Y":
                    return True
                elif answer and len(answer) == 1 and answer.upper() == "N":
                    return False
                else:
                    self.warning("Please set 'Y' for yes or 'N' for no")
                    answer = raw_input(msg)
        if type == SELECT:
            if len(args) > 1:
                print "\n".join("{0} : {1}".format(index+1,getattr(option,args[1])) for index, option in enumerate(args[0]))
            else:
                print "\n".join("{0} : {1}".format(index+1,option) for index, option in enumerate(args[0]))

            while True:
                msg    = self.colorstr("{0} [{1}-{2}]>>  ".format(message, 1, len(args[0])) , color)
                answer = raw_input(msg)
                if answer.isdigit():
                    answer = int(answer)
                    if answer <= len(args[0]) and answer >=1:
                        return (answer, args[0][answer-1])
        
        if type == PASSWORD:
            msg = self.colorstr("{0} >> ".format(message), color)
            return getpass.getpass(msg)

    def debug(self, message):             
        if DEBUG == True:
            self._print(message, colorama.Fore.CYAN)
        else:
            pass

    def output(self, message):
        self._print(message, type = OUTPUT)
    def trace(self, message):
        self._print(message, colorama.Fore.BLUE)
    
    def error(self, message):
        self._print(message, colorama.Fore.RED)

    def exception(self):
	if DEBUG:
            self.error(traceback.format_exc())
	else:
            self.error(traceback.format_exc().splitlines()[-1])

    def bug(self, message):
        self.error(message)
        self.warning('oops, there may be a bug in bae cli, please no hesitate send email to {support} report this, Please accept our apology for the inconvenience this matter have give you.' .format(support = BAE_SUPPORT))

    def success(self, message):
        self._print(message, colorama.Fore.GREEN)
    
    def suggestion(self, message):
        self._print(message, colorama.Fore.YELLOW)
        
    def warning(self, message):
        self._print(message, colorama.Fore.MAGENTA)

    def input(self, message):
        return self._print(message, colorama.Fore.GREEN, INPUT)

    def select(self, message, *args):
        return self._print(message, colorama.Fore.GREEN, SELECT, *args)

    def password(self, message):
        return self._print(message, colorama.Fore.GREEN, PASSWORD)

    def yes_or_no(self, message):
        return self._print(message, colorama.Fore.GREEN, YES_OR_NO)

g_messager = BaeMessage()
