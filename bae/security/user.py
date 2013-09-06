#-*- coding : utf-8 -*-

import base64
import os
import json

from Crypto.PublicKey import RSA
import Crypto.Cipher.PKCS1_v1_5 as PKCS

_pb = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCpwGVYBb6U41mM9FBliGDJoZGAaVF/snhFy+IkNIioCxpKhQdU1PMFAaODkeidBsRNaamPg8mISeMwWvwfRN4Fpyu7mIdMJ96Qu/+D+Hs5QVcbDfktxn7gvfaKUuI/+FNgcnJv16tW883er1vVv6mN55M9nwSTuOONe12AEhZCuwIDAQAB"

class BaiduUser:
    def __init__(self, username, password, isphone = False):
        self._username = username
        self._password = password
        self._isphone  = isphone

    def cipher(self):
        if self._isphone:
            isphone = "yes"
        else:
            isphone = "no"

        data = {"username" : self._username, "password" : self._password, "isphone" : isphone}        
        b64 = base64.decodestring(_pb)
        rsaobj = PKCS.new(RSA.importKey(b64))
        cipher = rsaobj.encrypt(json.dumps(data))
        b64c = base64.b64encode(cipher)
        return b64c

