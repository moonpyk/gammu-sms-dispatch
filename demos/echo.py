# coding=utf-8
from __future__ import print_function, unicode_literals

import os
import subprocess


def main(phone, message):
    subprocess.call(
        [
            "gammu-smsd-inject",
            "TEXT",
            phone,
            "-text",
            "Hey there, I'm replying : {0}".format(message),
        ]
    )


if __name__ == "__main__":
    main(os.environ["PHONE"], os.environ["MESSAGE"])
