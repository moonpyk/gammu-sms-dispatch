# coding=utf-8
from __future__ import print_function

import os
import subprocess
import sys
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


def open_config():
    cfg = ConfigParser()
    cfg.read(LOOKUP_TABLE)
    return cfg


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
        return -1


def exec_cmd(syscmd, parsed):
    args = syscmd.split(' ')
    args.append(parsed['phone'])
    args.append(parsed['message'])

    new_env = os.environ.copy()
    new_env["PHONE"] = parsed['phone']
    new_env["MESSAGE"] = parsed['message']

    return subprocess.call(args, env=new_env)


def notify_admin(admin_list, sms, was_parsed, final_code):
    if len(admin_list) == 0:
        return

    for phone in admin_list:
        if len(phone) == 0:
            continue

        send_sms(
            phone,
            '{0} : "{1}" [{2}, {3}]'.format(sms['phone'], sms['message'], was_parsed, final_code)
        )


def main():
    cfg = open_config()

    try:
        cmds = cfg.items('Commands')

    except NoSectionError:
        sys.exit(ERROR_CODES['ERR_CONFIG'])

    parsed = parse_sms()

    if len(parsed) == 0:
        sys.exit(ERROR_CODES['ERR_NO_SMS_FOUND'])

    adm = []

    try:
        adm = cfg.get('DEFAULT', 'admin').split(';')
    except NoOptionError:
        pass

    is_admin = parsed['phone'] in adm
    was_parsed = False
    final_code = 0

    command = parsed["message"].lower().split(' ')[0]

    for (order, syscmd) in cmds:
        if command == order:
            was_parsed = True
            final_code = exec_cmd(syscmd, parsed)
            break

    if not is_admin:
        notify_admin(adm, parsed, was_parsed, final_code)

    if not was_parsed:
        sys.exit(ERROR_CODES['ERR_NOT_PARSED'])

    if final_code != 0:
        sys.exit(ERROR_CODES['ERR_DISPATCH_CMD'])


if __name__ == '__main__':
    main()
