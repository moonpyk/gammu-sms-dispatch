# coding=utf-8
from __future__ import print_function

import logging
import os
import subprocess
import sys

logger = logging.getLogger('gammu-dispatch')

from ConfigParser import ConfigParser, NoSectionError, NoOptionError

LOOKUP_TABLE = [
    "./gammu-dispatch.conf",
    "~/gammu-dispatch.conf",
    "/etc/gammu-dispatch.conf"
]

ERROR_CODES = {
    'ERR_CONFIG': 1,
    'ERR_NO_SMS_FOUND': 2,
    'ERR_DISPATCH_CMD': 3,
    'ERR_NOT_PARSED': 4,
}


class GammuDispath(object):
    def __init__(self, cfg):
        self._cfg = cfg

        try:
            self._admins = cfg.get('DEFAULT', 'admin').split(';')
        except NoOptionError:
            self._admins = []

    def _is_admin(self, number):
        return number in self._admins

    def _notify_admin(self, sms, was_parsed, final_code):
        if len(self._admins) == 0:
            return

        for phone in self._admins:
            if len(phone) == 0:
                continue

            GammuDispath.send_sms(
                phone,
                '{0} : "{1}" [parsed:{2}, code:{3}]'.format(sms['phone'], sms['message'], was_parsed, final_code)
            )

    def dispatch(self):
        parsed = self.parse_sms()

        if len(parsed) == 0:
            logger.warn("No SMS found")
            return ERROR_CODES['ERR_NO_SMS_FOUND']

        try:
            cmds = self._cfg.items('Commands')

        except NoSectionError:
            logger.fatal("Unable to find the 'Commands' section")
            return ERROR_CODES['ERR_CONFIG']

        was_parsed = False
        final_code = 0

        command = parsed["message"].lower().split(' ')[0]

        logger.debug("Command : '{0}' from '{1}'".format(command, parsed['phone']))

        for (order, syscmd) in cmds:
            if command == order:
                logger.info("Found matching command, starting '{0}'".format(syscmd))
                was_parsed = True
                final_code = GammuDispath.exec_cmd(syscmd, parsed)
                break

        if not self._is_admin(parsed['phone']):
            logger.info("Phone number '{0}' is not an admin, notifying".format(parsed['phone']))
            self._notify_admin(parsed, was_parsed, final_code)

        if not was_parsed:
            logger.warning("Message was not parsed")
            return ERROR_CODES['ERR_NOT_PARSED']

        if final_code != 0:
            logger.warning("Message was parsed but the command returned exit code {0}".format(final_code))
            return ERROR_CODES['ERR_DISPATCH_CMD']

        return 0

    @staticmethod
    def parse_sms():
        if 'SMS_MESSAGES' not in os.environ:
            return {}

        numparts = int(os.environ['SMS_MESSAGES'])

        # Are there any decoded parts?
        if numparts == 0:
            return {}

        # Get all text parts
        text = ''
        for i in range(1, numparts + 1):
            varname = 'SMS_%d_TEXT' % i
            if varname in os.environ:
                text = text + os.environ[varname]

        return {
            'phone': os.environ['SMS_1_NUMBER'],
            'message': text.strip()
        }

    @staticmethod
    def send_sms(phone, message):
        # noinspection PyBroadException
        try:
            return subprocess.call([
                'gammu-smsd-inject',
                'TEXT',
                phone,
                '-text',
                message,
                '-len',
                str(len(message))
            ])

        except:
            logger.exception("An error occured while notifying '{0}' with message '{1}'".format(phone, message))
            return -1

    @staticmethod
    def exec_cmd(syscmd, parsed):
        args = syscmd.split(' ')
        args.append(parsed['phone'])
        args.append(parsed['message'])

        new_env = os.environ.copy()
        new_env["PHONE"] = parsed['phone']
        new_env["MESSAGE"] = parsed['message']

        return subprocess.call(args, env=new_env)


def open_config():
    cfg = ConfigParser()
    cfg.read(LOOKUP_TABLE)
    return cfg


def main():
    logging.raiseExceptions = False

    cfg = open_config()

    if 'GAMMU_DISPATCH_LOGGING' in os.environ:
        try:
            logging.basicConfig(level=os.environ['GAMMU_DISPATCH_LOGGING'])
        except ValueError:
            pass

    dspth = GammuDispath(cfg)

    sys.exit(dspth.dispatch())


if __name__ == '__main__':
    main()
