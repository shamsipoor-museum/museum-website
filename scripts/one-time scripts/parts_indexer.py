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

from attrs import frozen
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

PREFIX = "https://shamsipoor-museum.github.io/museum-website/fa_IR/parts/"


@frozen
class IndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""
    part_name: str = ""
    # part_pic: str = ""
    manufacturing_date: int = 0
    part_category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


@frozen
class PartTable:
    name: str = ""
    manufacturing_date: int = 0
    category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


@frozen
class PartsIndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[PartTable] = None


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


def extract_index_row(dirpath: str, f: str):
    path = osp.join(dirpath, f)
    f_text = read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return PartsIndexRow(
        filename=f,
        link=f,
        part_title=soup.title.text,
        table=PartTable(
            name=rows[0][1],
            manufacturing_date=rows[0][3],
            category=rows[1][1],
            manufacturer_name=rows[1][3],
            manufacturer_country=rows[2][1]
        )
    )


def extract_index(src_dir: str, exceptions: tuple):
    index = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".html"):
                if f in exceptions:
                    continue
                index.append(extract_index_row(dirpath, f))
    return index


def write_templated_data(data, template, path, mode="w", title="فهرست قطعات"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, index=data))


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    src_dir = src_dir if src_dir is not None else sys.argv[1]
    dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
    containing_dir = osp.normpath(osp.join(__file__, os.pardir))
    env = Environment(
        loader=FileSystemLoader(osp.join(containing_dir, "templates/parts")),
        autoescape=select_autoescape()
    )
    template = env.get_template("parts_index_template.html")

    index = extract_index(src_dir, exceptions=("index.html", "qr_codes.html"))
    write_templated_data(index, template, osp.join(dst_dir, "index.html"))


if __name__ == "__main__":
    main(src_dir="docs/fa_IR/parts", dst_dir="docs/fa_IR/parts")
