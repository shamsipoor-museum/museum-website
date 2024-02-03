# Copyright 2023 MohammadMohsen Akbarpoor Darabi (M. MAD)

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import os
from os import path as osp
from typing import Optional

import qrcode as qr

PREFIX = "https://shamsipoor-museum.github.io/museum-website/fa_IR/parts/"


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None,
         dry_run: bool = True):
    src_dir = src_dir if src_dir is not None else sys.argv[1]
    dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
    exceptions = ("index.html", )
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".html"):
                if f in exceptions:
                    continue
                f = osp.splitext(f)[0]
                print(PREFIX + f)
                if not dry_run:
                    qrcode = qr.make(PREFIX + f)
                    qrcode.save(osp.join(dst_dir, f + ".png"))


if __name__ == "__main__":
    main(src_dir="docs/fa_IR/parts", dst_dir="docs/fa_IR/parts/qr_codes", dry_run=True)
