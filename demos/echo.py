# coding=utf-8
from __future__ import print_function, unicode_literals

import sys
import subprocess

def main(phone, message):
    subprocess.call(["gammu-smsd-inject", "TEXT", phone, "-text", message])


if __name__ == '__main__':
    print([sys.argv[0], sys.argv[1]])
    main(sys.argv[0], sys.argv[1])
