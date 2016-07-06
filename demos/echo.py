# coding=utf-8
from __future__ import print_function, unicode_literals

import sys

import subprocess


def main(phone, message):
    subprocess.call(["gammu-smsd-inject", "TEXT", phone, "-text", "Coucou je te réponds"])


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1])
