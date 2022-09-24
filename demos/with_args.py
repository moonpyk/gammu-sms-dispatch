# coding=utf-8
from __future__ import print_function, unicode_literals

import os


def main(phone, message):
    # la variable est un tableau qui contient dans chaque cellule les arguments
    arguments = message.split(" ")[1:]


if __name__ == "__main__":
    main(os.environ["PHONE"], os.environ["MESSAGE"])
