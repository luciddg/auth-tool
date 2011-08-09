from turbomail.control import interface
from turbomail import Message

turbomail_config = {
  'mail.on' : True,
  'mail.transport' : 'smtp',
  'mail.smtp.server' : 'localhost',
}


def sendMsg(addr,msg):
  interface.start(turbomail_config)
  message = Message("sysadmin@luciddg.com", addr, "password reset")
  message.plain = msg
  message.send()
  interface.stop()

