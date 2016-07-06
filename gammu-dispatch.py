from __future__ import print_function, unicode_literals
import os
import sys
from ConfigParser import ConfigParser, NoSectionError

import subprocess

LOOKUP_TABLE = [
    "/etc/gammu-dispatch.conf"
    "~/gammu-dispatch.conf",
    "./gammu-dispatch.conf",
]


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


def exec_cmd(syscmd, parsed):
    args = syscmd.split(' ')
    args.append(parsed['phone'])
    args.append(parsed['message'])

    if subprocess.call(args) != 0:
        sys.exit(3)


def main(argv):
    cfg = open_config()

    try:
        cmds = cfg.items('Commands')

    except NoSectionError:
        sys.exit(1)

    parsed = parse_sms()

    if len(parsed) == 0:
        sys.exit(2)

    for (order, syscmd) in cmds:
        if parsed["message"].lower() == order:
            exec_cmd(syscmd, parsed)


if __name__ == '__main__':
    main(sys.argv)
