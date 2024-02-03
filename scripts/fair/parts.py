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

import os
from os import path as osp
# from datetime import date
from typing import Optional, Union, Type, Callable, Tuple, Dict

from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import frontmatter as fm

import blogger as b
from . import common as c

PREFIX = c.FA_IR_PREFIX + "parts/"


@frozen
class PartTable:
    name: str = ""
    manufacturing_date: int = 0
    category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


# (slots=False) is there because we have to have access to __dict__, and
# __dict__ won't be available when using slots
@frozen(slots=False)
class PartData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[PartTable] = None
    explanation_paragraphs: Optional[Union[str, Tuple[str]]] = None


@frozen
class PartsIndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[PartTable] = None


def extract_table_from_md(loaded_file: fm.Post) -> PartTable:
    return PartTable(
        name=loaded_file["name"],
        manufacturing_date=loaded_file["manufacturing_date"],
        category=loaded_file["category"],
        manufacturer_name=loaded_file["manufacturer_name"],
        manufacturer_country=loaded_file["manufacturer_country"]
    )


def extract_data_from_md(dirpath, f) -> PartData:
    fl = fm.load(osp.join(dirpath, f))
    # print("[debug]", fl.__dict__)
    return PartData(
        title=fl["title"],
        header=fl["header"],
        pic=fl["pic"],
        table=extract_table_from_md(fl),
        explanation_paragraphs=fl.content
    )


def extract_data(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> Dict[str, PartData]:
    exceptions = b.compile_re_collection(exceptions)
    pd_dict = dict()
    for dirpath, dirnames, filenames in os.walk(sec.input_path):
        for f in filenames:
            if f.endswith(".md"):
                if b.search_re_collection(exceptions, f):
                    continue
                pd_dict[f] = sec.extract_data_from_md(dirpath, f)
    return pd_dict


def write_data(sec: b.SecSpec, pd_dict: Dict[str, PartData]):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.basename(sec.template_path))
    for filename in pd_dict:
        # print(osp.join(sec.output_path, filename.replace(".md", ".html")),
        #       pd_dict[filename], sep="\n---\n", end="\n----------\n")
        with open(osp.join(sec.output_path, filename.replace(".md", ".html")), mode="w") as f:
            f.write(template.render(pd_dict[filename].__dict__))


# Index

def extract_table_from_soup(soup: BeautifulSoup) -> PartTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return PartTable(
        name=rows[0][1],
        manufacturing_date=rows[0][3],
        category=rows[1][1],
        manufacturer_name=rows[1][3],
        manufacturer_country=rows[2][1]
    )


def extract_table_from_soup_no_escape(soup: BeautifulSoup) -> PartTable:
    rows = [str(row).strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    # print(rows)
    return PartTable(
        name=rows[0][2][9:-5],  # removing "</b><br/>" from start and "</td>" from end
        manufacturing_date=rows[0][4][9:-5],
        category=rows[1][2][9:-5],
        manufacturer_name=rows[1][4][9:-5],
        manufacturer_country=rows[2][2][9:-5]
    )


def extract_index_row(dirpath: str, f: str) -> PartsIndexRow:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return PartsIndexRow(
        filename=f,
        link=f,
        part_title=soup.title.text,
        table=extract_table_from_soup(soup)
    )


def extract_index(sec: b.SecSpec, exceptions: Tuple[str] = b.GE) -> tuple:
    exceptions = b.compile_re_collection(exceptions)
    index = []
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if b.search_re_collection(exceptions, f):
                    continue
                index.append(extract_index_row(dirpath, f))
    return tuple(index)


def write_index(sec: b.SecSpec, index: tuple, title="فهرست قطعات"):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.basename(sec.index_template_path))
    with open(osp.join(sec.output_path, sec.index_filename), mode="w") as f:
        f.write(template.render(title=title, index=index))


# Reverse


def extract_data_from_html(dirpath: str, f: str, markdownify: bool = False) -> PartData:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    # ep = [p.text for p in e.find_all("p") for e in soup.body.find_all("div", {"class": "fa-IR-explanation"})]
    # ep = []
    # for e in soup.body.find_all("div", {"class": "fa-IR-explanation"}):
    #     for p in e.find_all("p"):
    #         # print(md(str(p)))
    #         ep.append(md(str(p)) if markdownify else p.text)
    return PartData(
        title=str(soup.title)[7:-8],
        header=str(soup.h1)[43:-5],  # TODO
        pic=soup.img["src"],
        table=extract_table_from_soup_no_escape(soup),
        explanation_paragraphs=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )
