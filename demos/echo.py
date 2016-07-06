# coding=utf-8
from __future__ import print_function, unicode_literals

import sys

import subprocess


def main(phone, message):
    subprocess.call(["gammu-smsd-inject", "TEXT", phone, "-text", message])


if __name__ == '__main__':
    argv_ = sys.argv[1:]
    print(argv_)
    main(argv_[0], argv_[1])
