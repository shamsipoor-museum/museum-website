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

from jinja2 import Environment, FileSystemLoader, select_autoescape

PREFIX = "https://shamsipoor-museum.github.io/museum-website/fa_IR/parts/"


def extract_qr_table(src_dir: str, rows: int = 5, cols: int = 4,
                     exceptions: tuple = ("index.png", )) -> tuple:
    pages = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".png"):
                if f in exceptions:
                    continue
                if len(pages) == 0 or (len(pages[-1]) >= rows and len(pages[-1][-1]) >= cols):
                    pages.append([])
                table = pages[-1]
                # print("[$$$]", f, table)
                table_len = len(table)
                if table_len <= rows:
                    if (table_len == 0 or len(table[-1]) >= cols) and table_len + 1 <= rows:
                        table.append([])
                    if len(table[-1]) < cols:
                        table[-1].append(osp.splitext(osp.basename(f))[0])
    return tuple(pages)


def write_qr_table(data, template, path, mode="w", title="QR Codes"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, table=data))


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None,
         dry_run: bool = True):
    src_dir = src_dir if src_dir is not None else sys.argv[1]
    dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
    containing_dir = osp.normpath(osp.join(__file__, os.pardir))
    env = Environment(
        loader=FileSystemLoader(osp.join(containing_dir, "templates")),
        autoescape=select_autoescape()
    )
    template = env.get_template("qr_codes_template.html")
    pages = extract_qr_table(src_dir, rows=5, cols=4)
    print(50*"=")
    for table in pages:
        print("[table]", table, "^^^", len(table))
        for row in table:
            print("[row]", row, "^^^", len(row))
    for i, table in enumerate(pages, start=1):
        write_qr_table(table, template, osp.join(dst_dir, f"qr_codes_{i}.html"), title=f"QR Codes {i}")



if __name__ == "__main__":
    main(src_dir="docs/fa_IR/parts/qr_codes", dst_dir="docs/fa_IR/parts/qr_codes", dry_run=True)
