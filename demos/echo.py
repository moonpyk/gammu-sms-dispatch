# coding=utf-8
from __future__ import print_function, unicode_literals

import sys
import subprocess


def main(phone, message):
    subprocess.call(["gammu-smsd-inject", "TEXT", phone, "-text", "Coucou je te réponds"])


if __name__ == '__main__':
    rargs = sys.argv[1:]
    main(rargs[0], rargs[1])
