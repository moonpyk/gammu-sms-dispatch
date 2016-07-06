# coding=utf-8
from __future__ import print_function, unicode_literals

import os


def main(phone, message):
    # Code of the program here
    print(["Coucou", phone, message])

if __name__ == '__main__':
    main(os.environ["PHONE"], os.environ["MESSAGE"])
