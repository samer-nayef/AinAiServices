import configparser
import os

from cryptography.fernet import Fernet

import api


def generateKey(text):
    key = Fernet.generate_key()
    cfg = api.cfg
    cfg.set('token', 'text', text)
    cfg.set('token', 'key', key.decode("UTF-8"))
    value = encrypt_text(text=text, key=key)
    cfg.set('token', 'value', value)
    with open(api.ROOT_DIR+'\\configuration.cfg', 'w') as configfile:
        cfg.write(configfile)

    configfile.close()

    return value

def encrypt_text(text ,key):
    f = Fernet(key)
    encrypted_text = f.encrypt(bytes(text, "UTF-8"))

    return encrypted_text.decode()

    # key = b'hHaFKFxd2r51SiHmiKWov6JX3T-zIUxBSdmGtycNVvs='


def decrypt_text(self ,token):
    try:
        f = Fernet(self.getflaskkey())
        return f.decrypt(bytes(token, "UTF-8")).decode()
    except BaseException as e:
        return "Invalid Token"

def getflaskkey(self):
    cfg = configparser.ConfigParser()
    cfg.read('services/configuration.cfg')
    return str.encode(cfg.get('token', 'key'))