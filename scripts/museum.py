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


#  ____       _            _   _     _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/


@frozen
class ScientistTable:
    name: Optional[str] = None
    # birth_date: Optional[date] = None
    # birth_location: Optional[str] = None
    born: Optional[str] = None
    # death_date: Optional[date] = None
    # death_location: Optional[str] = None
    died: Optional[str] = None
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
class ScientistsIndexRow:
    filename: str = ""
    link: str = ""
    scientist_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[ScientistTable] = None


#  ____            _
# |  _ \ __ _ _ __| |_ ___
# | |_) / _` | '__| __/ __|
# |  __/ (_| | |  | |_\__ \
# |_|   \__,_|_|   \__|___/


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


#  ____       _            _   _     _         ___           _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___  |_ _|_ __   __| | _____  __
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|  | || '_ \ / _` |/ _ \ \/ /
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \  | || | | | (_| |  __/>  <
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/ |___|_| |_|\__,_|\___/_/\_\


def fa_ir_scientists_extract_table_from_soup(soup: BeautifulSoup) -> ScientistTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return ScientistTable(
        name=rows[0][1],
        born=rows[0][3],
        died=rows[1][1],
        nationality=rows[1][3],
        alma_mater=rows[2][1],
        known_for=rows[2][3],
        awards=rows[3][1],
        tags=rows[3][3]
    )


def fa_ir_scientists_extract_index_row(dirpath: str, f: str):
    path = osp.join(dirpath, f)
    f_text = blogger.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return ScientistsIndexRow(
        filename=f,
        link=f,
        scientist_title=soup.title.text,
        table=fa_ir_scientists_extract_table_from_soup(soup)
    )


def fa_ir_scientists_extract_index(sec: blogger.SecSpec, exceptions: Tuple[str] = blogger.GE) -> tuple:
    exceptions = blogger.compile_re_collection(exceptions)
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if blogger.search_re_collection(exceptions, f):
                    continue
                index.append(fa_ir_scientists_extract_index_row(dirpath, f))
    return tuple(index)


def fa_ir_scientists_write_index(sec: blogger.SecSpec, index: tuple, title="فهرست دانشمندان"):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    with open(osp.join(sec.output_path, sec.index_filename), mode="w") as f:
        f.write(template.render(title=title, index=index))


#  ____            _         ___           _
# |  _ \ __ _ _ __| |_ ___  |_ _|_ __   __| | _____  __
# | |_) / _` | '__| __/ __|  | || '_ \ / _` |/ _ \ \/ /
# |  __/ (_| | |  | |_\__ \  | || | | | (_| |  __/>  <
# |_|   \__,_|_|   \__|___/ |___|_| |_|\__,_|\___/_/\_\


def fa_ir_parts_extract_table_from_soup(soup: BeautifulSoup) -> PartTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return PartTable(
        name=rows[0][1],
        manufacturing_date=rows[0][3],
        category=rows[1][1],
        manufacturer_name=rows[1][3],
        manufacturer_country=rows[2][1]
    )


def fa_ir_parts_extract_index_row(dirpath: str, f: str):
    path = osp.join(dirpath, f)
    f_text = blogger.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return PartsIndexRow(
        filename=f,
        link=f,
        part_title=soup.title.text,
        table=fa_ir_parts_extract_table_from_soup(soup)
    )


def fa_ir_parts_extract_index(sec: blogger.SecSpec, exceptions: Tuple[str] = blogger.GE) -> tuple:
    exceptions = blogger.compile_re_collection(exceptions)
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if blogger.search_re_collection(exceptions, f):
                    continue
                index.append(fa_ir_parts_extract_index_row(dirpath, f))
    return tuple(index)


def fa_ir_parts_write_index(sec: blogger.SecSpec, index: tuple, title="فهرست قطعات"):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    with open(osp.join(sec.output_path, sec.index_filename), mode="w") as f:
        f.write(template.render(title=title, index=index))


document_root = blogger.SecSpec(name="root", output_path="docs", url_prefix=PREFIX)
fa_ir_root = blogger.SecSpec(name="fa_ir", output_path="docs/fa_IR", url_prefix=FA_IR_PREFIX)
fa_ir_parts = blogger.SecSpec(
    name="fa_ir_parts",
    output_path="docs/fa_IR/parts",
    url_prefix=FA_IR_PARTS_PREFIX,
    input_path="scripts/original_content/fa_IR/parts",
    data_spec=PartData,
    template_path="scripts/templates/fa_IR/parts/parts_template.html",
    extract_data=None,
    write_data=None,
    index_template_path="scripts/templates/fa_IR/parts/parts_index_template.html",
    extract_index=fa_ir_parts_extract_index,
    write_index=fa_ir_parts_write_index,
    qr_template_path="scripts/templates/fa_IR/parts/qr_pages_template.html",
)
fa_ir_scientists = blogger.SecSpec(
    name="fa_ir_scientists",
    output_path="docs/fa_IR/scientists",
    url_prefix=FA_IR_SCIENTISTS_PREFIX,
    input_path="scripts/original_content/fa_IR/scientists",
    data_spec=ScientistData,
    template_path="scripts/templates/fa_IR/scientists/scientists_template.html",
    extract_data=None,
    write_data=None,
    index_template_path="scripts/templates/fa_IR/scientists/scientists_index_template.html",
    extract_index=fa_ir_scientists_extract_index,
    write_index=fa_ir_scientists_write_index,
    qr_template_path="scripts/templates/fa_IR/parts/qr_pages_template.html",
)
fa_ir_root.sub_specs = [fa_ir_parts, fa_ir_scientists]
document_root.sub_specs = [fa_ir_root]


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    blogger.generate_index(fa_ir_parts, exceptions=blogger.GE)
    blogger.generate_qr_codes(fa_ir_parts, exceptions=blogger.GE, qr_pages_exceptions=blogger.GE)

    blogger.generate_index(fa_ir_scientists, exceptions=blogger.GE)
    blogger.generate_qr_codes(fa_ir_scientists, exceptions=blogger.GE, qr_pages_exceptions=blogger.GE)


if __name__ == "__main__":
    main()
