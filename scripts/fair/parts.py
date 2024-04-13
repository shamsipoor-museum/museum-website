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
from typing import Optional, Union, Collection

from attrs import asdict, frozen
from bs4 import BeautifulSoup
import frontmatter as fm

import blogger as b
from . import common as c

PREFIX = c.FA_IR_PREFIX + "parts/"


@frozen
class PartTable:
    name: str = ""
    manufacturing_date: Union[int, str] = ""
    category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""


@frozen
class PartData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[PartTable] = None
    explanation_paragraphs: Optional[Union[str, Collection[str]]] = None


@frozen
class PartsIndexRow:
    filename: str = ""
    link: str = ""
    part_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[PartTable] = None


def md_table_extractor(loaded_file: fm.Post) -> PartTable:
    return PartTable(
        name=loaded_file["name"],
        manufacturing_date=loaded_file["manufacturing_date"],
        category=loaded_file["category"],
        manufacturer_name=loaded_file["manufacturer_name"],
        manufacturer_country=loaded_file["manufacturer_country"]
    )


def md_data_extractor(dirpath: str, f: str) -> PartData:
    fl = fm.load(osp.join(dirpath, f))
    # print("[debug]", asdict(fl))
    return PartData(
        title=fl["title"],
        header=fl["header"],
        pic=fl["pic"],
        table=md_table_extractor(fl),
        explanation_paragraphs=fl.content
    )


# Index


def soup_table_extractor(soup: BeautifulSoup) -> PartTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return PartTable(
        name=rows[0][1],
        manufacturing_date=rows[0][3],
        category=rows[1][1],
        manufacturer_name=rows[1][3],
        manufacturer_country=rows[2][1]
    )


def escapeless_soup_table_extractor(soup: BeautifulSoup) -> PartTable:
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


def index_row_extractor(dirpath: str, f: str) -> PartsIndexRow:
    path = osp.join(dirpath, f)
    f_text = b.file_reader(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return PartsIndexRow(
        filename=f,
        link=f,
        part_title=soup.title.text,
        table=soup_table_extractor(soup)
    )


# Reverse


def html_data_extractor(dirpath: str, f: str, markdownify: bool = False) -> PartData:
    path = osp.join(dirpath, f)
    f_text = b.file_reader(path)
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
        table=escapeless_soup_table_extractor(soup),
        explanation_paragraphs=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )
