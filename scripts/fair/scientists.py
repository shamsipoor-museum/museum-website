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

from os import path as osp
from typing import Collection, Optional, Union

from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
import frontmatter as fm

import blogger as b
from . import common as c

PREFIX = c.FA_IR_PREFIX + "scientists/"

@frozen
class ScientistTable:
    name: Optional[str] = None
    # birth_date: Optional[date] = None
    # birth_location: Optional[str] = None
    born: Optional[str] = None
    # death_date: Optional[date] = None
    # death_location: Optional[str] = None
    died: Optional[str] = None
    gender: Optional[bool] = None
    nationality: Optional[Union[str, Collection[str]]] = None  # They can have multiple citizenships
    alma_mater: Optional[Union[str, Collection[str]]] = None
    known_for: Optional[Union[str, Collection[str]]] = None
    awards: Optional[Union[str, Collection[str]]] = None
    tags: Optional[Union[str, Collection[str]]] = None


# (slots=False) is there because we have to have access to __dict__, and
# __dict__ won't be available when using slots
@frozen(slots=False)
class ScientistData:
    title: Optional[str] = None
    header: Optional[str] = None
    pic: Optional[str] = None
    table: Optional[ScientistTable] = None
    bio_summary: Optional[Union[str, Collection[str]]] = None
    bio: Optional[Union[str, Collection[str]]] = None


@frozen
class ScientistsIndexRow:
    filename: str = ""
    link: str = ""
    scientist_title: str = ""  # There is also a title on top of the page
    # pic: str = ""
    table: Optional[ScientistTable] = None


def md_table_extractor(loaded_file: fm.Post) -> ScientistTable:
    return ScientistTable(
        name=loaded_file["name"],
        born=c.persian_stringifier(loaded_file["born"]),
        died=c.persian_stringifier(loaded_file["died"]),
        gender=loaded_file["gender"],
        nationality=c.persian_stringifier(loaded_file["nationality"]),
        alma_mater=c.persian_stringifier(loaded_file["alma_mater"]),
        known_for=c.persian_stringifier(loaded_file["known_for"]),
        awards=c.persian_stringifier(loaded_file["awards"]),
        tags=c.persian_stringifier(loaded_file["tags"])
    )


def md_data_extractor(dirpath, f) -> ScientistData:
    fl = fm.load(osp.join(dirpath, f))
    return ScientistData(
        title=fl["title"],
        header=fl["header"],
        pic=fl["pic"],
        table=md_table_extractor(fl),
        bio=fl.content
    )


# Index


def soup_table_extractor(soup: BeautifulSoup) -> ScientistTable:
    rows = [row.text.strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return ScientistTable(
        name=rows[0][1],
        born=rows[0][3],
        died=rows[1][1],
        gender=True if rows[1][3] == "مرد" else False,
        nationality=rows[2][1],
        alma_mater=rows[2][3],
        known_for=rows[3][1],
        awards=rows[3][3],
        tags=rows[4][1]
    )


def escapeless_soup_table_extractor(soup: BeautifulSoup) -> ScientistTable:
    rows = [str(row).strip("\n").replace("\n", ":").split(":")
            for row in soup.find_all("tr")]
    return ScientistTable(
        name=rows[0][2][9:-5],  # removing "</b><br/>" from start and "</td>" from end
        born=rows[0][4][9:-5],
        died=rows[1][2][9:-5],
        gender=True if rows[1][4][9:-5] == "مرد" else False,
        nationality=rows[2][2][9:-5],
        alma_mater=rows[2][4][9:-5],
        known_for=rows[3][2][9:-5],
        awards=rows[3][4][9:-5],
        tags=rows[4][2][9:-5]
    )


def index_row_extractor(dirpath: str, f: str) -> ScientistsIndexRow:
    path = osp.join(dirpath, f)
    f_text = b.file_reader(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return ScientistsIndexRow(
        filename=f,
        link=f,
        scientist_title=soup.title.text,
        table=soup_table_extractor(soup)
    )


# Reverse


def html_data_extractor(dirpath: str, f: str, markdownify: bool = False) -> ScientistData:
    path = osp.join(dirpath, f)
    f_text = b.file_reader(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return ScientistData(
        title=soup.title.text,
        header=soup.h1.text,  # TODO
        pic=soup.img["src"],
        table=escapeless_soup_table_extractor(soup),
        bio=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )
