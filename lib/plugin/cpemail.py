# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from urlparse import urljoin

import cherrypy
from cherrypy.process import wspbus, plugins

__all__ = ['EmailEnginePlugin']

class EmailEnginePlugin(plugins.SimplePlugin):
    """
    The EmailEnginePlugin is used to send password reset and username
    reminder emails.
    """


    def __init__(self, bus,
                 server='localhost',
                 port=25,
                 user=None,
                 password=None,
                 fromaddr=None,
                 subject=None):
        plugins.SimplePlugin.__init__(self, bus)
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.fromaddr = fromaddr
        self.subject = subject

    def start(self):
        self.bus.log('Starting up email plugin')
        self.bus.subscribe('email-send-reset', self._send_reset_email)
        self.bus.subscribe('email-send-username', self._send_username_email)

    def stop(self):
        self.bus.log('Stopping email plugin')
        self.bus.unsubscribe('email-send-reset', self._send_reset_email)
        self.bus.unsubscribe('email-send-username', self._send_username_email)
        self.server = None
        self.port = None
        self.user = None
        self.password = None
        self.fromaddr = None
        self.subject = None

    def _send_reset_email(self, user):
        """
        Send password reset email to given email address
        """

        username = user['uid'][0]
        token = cherrypy.engine.publish('token-gen', username).pop()
        base_url = urljoin('https://',cherrypy.request.base, '/reset')
        user['reset_url'] = urljoin(base_url, '?token={0}&username={1}'.format(token, username))

        template = cherrypy.config.get('email', {}).get('template', 'email')
        html = cherrypy.engine.publish('lookup-template', '{0}.html'.format(template)).pop()
        txt = cherrypy.engine.publish('lookup-template', '{0}.txt'.format(template)).pop()
        html_body = html.render(user=user)
        txt_body = txt.render(user=user)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = (' ').join([self.subject, 'Password Reset'])
        msg['From'] = self.fromaddr
        msg['To'] = user['mail'][0]
        part1 = MIMEText(txt_body, 'plain')
        part2 = MIMEText(html_body, 'html')

        msg.attach(part1)
        msg.attach(part2)

        mailclient = smtplib.SMTP(self.server, self.port)
        try:
            if self.user and self.password:
                mailclient.login(self.user, self.password)

            mailclient.sendmail(msg['From'], msg['To'], msg.as_string())
        except (smtplib.SMTPHeloError,
                smtplib.SMTPAuthenticationError,
                smtplib.SMTPException
               ) as e:
            self.bus.log('Unable to send email.  Error: {0}'.format(e.message['desc'] if 'desc' in e.message else e), 40) # pylint: disable=C0301
        finally:
            mailclient.quit()

    def _send_username_email(self, user):
        """
        Send username reminder email to given email address
        """
        username = user['uid'][0]
        base_url = urljoin('https://',cherrypy.request.base, '/')
        user['login_url'] = urljoin(base_url, '?username={0}'.format(username))

        template = cherrypy.config.get('email', {}).get('template', 'email')
        html = cherrypy.engine.publish('lookup-template', '{0}.html'.format(template)).pop()
        txt = cherrypy.engine.publish('lookup-template', '{0}.txt'.format(template)).pop()
        html_body = html.render(user=user)
        txt_body = txt.render(user=user)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = (' ').join([self.subject, 'Username Reminder'])
        msg['From'] = self.fromaddr
        msg['To'] = user['mail'][0]
        part1 = MIMEText(txt_body, 'plain')
        part2 = MIMEText(html_body, 'html')

        msg.attach(part1)
        msg.attach(part2)

        mailclient = smtplib.SMTP(self.server, self.port)
        try:
            if self.user and self.password:
                mailclient.login(self.user, self.password)

            mailclient.sendmail(msg['From'], msg['To'], msg.as_string())
        except (smtplib.SMTPHeloError,
                smtplib.SMTPAuthenticationError,
                smtplib.SMTPException
               ) as e:
            self.bus.log('Unable to send email.  Error: {0}'.format(e.message['desc'] if 'desc' in e.message else e), 40) # pylint: disable=C0301
        finally:
            mailclient.quit()
