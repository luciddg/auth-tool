from turbomail.control import interface
from turbomail import Message
from lib import msgtpl
import string

baseURL = 'https://password.office.luciddg.com'

turbomail_config = {
  'mail.on' : True,
  'mail.transport' : 'smtp',
  'mail.smtp.server' : 'localhost',
}


def sendMsg(addr,token):
  body = string.Template(msgtpl.message).substitute(baseURL=baseURL,token=token)
  interface.start(turbomail_config)
  message = Message("sysadmin@luciddg.com", addr, "password reset")
  message.plain = body
  message.send()
  interface.stop()

