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
from datetime import date
from typing import Optional, Union, Type, Callable, Tuple

from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

import blogger

PREFIX = "https://shamsipoor-museum.github.io/museum-website/"
FA_IR_PREFIX = PREFIX + "fa_IR/"
FA_IR_PARTS_PREFIX = FA_IR_PREFIX + "parts/"
FA_IR_SCIENTISTS_PREFIX = FA_IR_PREFIX + "scientists/"


@frozen
class ScientistTable:
    name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_location: Optional[str] = None
    death_date: Optional[date] = None
    death_location: Optional[str] = None
    nationality: Optional[Union[str, tuple]] = None
    alma_mater: Optional[Union[str, tuple]] = None
    known_for: Optional[Union[str, tuple]] = None
    awards: Optional[Union[str, tuple]] = None
    tags: Optional[tuple] = None


@frozen
class ScientistData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[ScientistTable] = None
    bio_summary: Optional[Union[str, tuple]] = None
    bio: Optional[Union[str, tuple]] = None


@frozen
class PartTable:
    name: str = ""
    manufacturing_date: int = 0
    category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


@frozen
class PartData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[PartTable] = None
    explanation_paragraphs: Optional[Union[str, tuple]] = None


@frozen
class PartsIndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[PartTable] = None


def fa_ir_parts_extract_index_row(dirpath: str, f: str):
    path = osp.join(dirpath, f)
    f_text = blogger.read_file(path)
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


def fa_ir_parts_extract_index(sec: blogger.SecSpec, exceptions: Optional[Tuple[str]] = None) -> tuple:
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if exceptions is not None and f in exceptions:
                    continue
                index.append(fa_ir_parts_extract_index_row(dirpath, f))
    return tuple(index)


def fa_ir_parts_write_index(sec: blogger.SecSpec, index: tuple):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    # print(osp.dirname(sec.index_template_path))
    # print(osp.basename(sec.index_template_path))
    # print(index)
    with open(osp.join(sec.output_path, "index.html"), mode="w") as f:
        f.write(template.render(title="فهرست قطعات", index=index))


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    document_root = blogger.SecSpec(name="root", output_path="docs", url_prefix=PREFIX)
    fa_ir_root = blogger.SecSpec(name="fa_ir", output_path="docs/fa_IR", url_prefix=FA_IR_PREFIX)
    fa_ir_parts = blogger.SecSpec(
        name="fa_ir_parts",
        output_path="docs/fa_IR/parts",
        url_prefix=FA_IR_PARTS_PREFIX,
        data_spec=PartData,
        template_path="scripts/templates/parts/parts_template.html",
        extract_data=None,
        write_data=None,
        index_template_path="scripts/templates/parts/parts_index_template.html",
        extract_index=fa_ir_parts_extract_index,
        write_index=fa_ir_parts_write_index,
        qr_dirname="docs/fa_IR/parts/qr_codes",
        qr_template_path="scripts/templates/parts/qr_pages_template.html",
        qr_pages_dirname="docs/fa_IR/parts/qr_codes/pages"
    )
    fa_ir_scientists = blogger.SecSpec(
        name="fa_ir_scientists",
        output_path="docs/fa_IR/scientists",
        url_prefix=FA_IR_SCIENTISTS_PREFIX,
    )
    fa_ir_root.sub_specs = [fa_ir_parts, fa_ir_scientists]
    document_root.sub_specs = [fa_ir_root]

    ge = ("index.html", "qr_codes.html")
    # fa_ir_parts.write_index(fa_ir_parts, fa_ir_parts.extract_index(fa_ir_parts, exceptions=("index.html", "qr_codes.html")))
    blogger.generate_index(fa_ir_parts, exceptions=("index.html", "qr_codes.html"))

    # blogger.generate_qr_codes(fa_ir_parts, exceptions=ge, qr_pages_exceptions=ge)

    # src_dir = src_dir if src_dir is not None else sys.argv[1]
    # dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
    # containing_dir = osp.normpath(osp.join(__file__, os.pardir))
    # env = Environment(
    #     loader=FileSystemLoader(osp.join(containing_dir, "templates")),
    #     autoescape=select_autoescape()
    # )
    # template = env.get_template("parts_index_template.html")

    # index = extract_index(src_dir, exceptions=("index.html", "qr_codes.html"))
    # write_templated_data(index, template, osp.join(dst_dir, "index.html"), title="فهرست قطعات")


if __name__ == "__main__":
    # main(src_dir="docs/fa_IR/parts", dst_dir="docs/fa_IR/parts")
    main()
    # pass
