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
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
from markdownify import markdownify as md

import blogger as b
import museum as m


#  ____       _            _   _     _
# / ___|  ___(_) ___ _ __ | |_(_)___| |_ ___
# \___ \ / __| |/ _ \ '_ \| __| / __| __/ __|
#  ___) | (__| |  __/ | | | |_| \__ \ |_\__ \
# |____/ \___|_|\___|_| |_|\__|_|___/\__|___/


def fa_ir_scientists_extract_data_from_html(dirpath: str, f: str, markdownify: bool = False) -> m.ScientistData:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    return m.ScientistData(
        title=soup.title.text,
        header=soup.h1.text,  # TODO
        pic=soup.img["src"],
        table=m.fa_ir_scientists_extract_table_from_soup_no_escape(soup),
        bio=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )


def fa_ir_scientists_write_data_to_md(pd: m.ScientistData, template: Template, path: str, mode: str = "w"):
    with open(path, mode) as f:
        f.write(template.render(pd.__dict__))


#  ____            _
# |  _ \ __ _ _ __| |_ ___
# | |_) / _` | '__| __/ __|
# |  __/ (_| | |  | |_\__ \
# |_|   \__,_|_|   \__|___/


def fa_ir_parts_extract_data_from_html(dirpath: str, f: str, markdownify: bool = False) -> m.PartData:
    path = osp.join(dirpath, f)
    f_text = b.read_file(path)
    soup = BeautifulSoup(f_text, "html.parser")
    # ep = [p.text for p in e.find_all("p") for e in soup.body.find_all("div", {"class": "fa-IR-explanation"})]
    # ep = []
    # for e in soup.body.find_all("div", {"class": "fa-IR-explanation"}):
    #     for p in e.find_all("p"):
    #         # print(md(str(p)))
    #         ep.append(md(str(p)) if markdownify else p.text)
    return m.PartData(
        title=soup.title.text,
        header=soup.h1.text,  # TODO
        pic=soup.img["src"],
        table=m.fa_ir_parts_extract_table_from_soup_no_escape(soup),
        explanation_paragraphs=str(
            soup.body.find("div", {"class": "fa-IR-explanation"})
        ).lstrip('<div class="fa-IR-explanation">').rstrip('</div>')
    )


def fa_ir_parts_write_data_to_md(pd: m.PartData, template: Template, path: str, mode: str = "w"):
    with open(path, mode) as f:
        f.write(template.render(pd.__dict__))


def html_to_md(sec: b.SecSpec, extract_data: Callable, write_data: Callable,
               template_path: str, exceptions: Optional[Tuple[str]] = b.GE,
               dry_run: bool = True):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.basename(template_path))

    exceptions = b.compile_re_collection(exceptions)
    # data_dict = dict()
    for dirpath, dirnames, filenames in os.walk(sec.output_path):
        for f in filenames:
            if f.endswith(".html"):
                if b.search_re_collection(exceptions, f):
                    continue
                extracted_data = extract_data(dirpath, f)
                if dry_run:
                    print(dirpath, f, f.replace(".html", ".md"), sep=" --- ")
                    print(extracted_data)
                    print("---")
                else:
                    write_data(extracted_data, template,
                               osp.join(sec.input_path, f.replace(".html", ".md")))


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None,
         template_path: Optional[str] = None, dry_run: bool = True):
    src_dir = src_dir if src_dir is not None else sys.argv[1]
    dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
    template_path = template_path if template_path is not None else sys.argv[2]
    env = Environment(
        loader=FileSystemLoader(osp.dirname(template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template("parts_template.md")


if __name__ == "__main__":
    # main(src_dir=m.fa_ir_parts.output_path, dst_dir=m.fa_ir_parts.input_path,
    #      template_path=m.fa_ir_parts.template_path)
    # html_to_md(m.fa_ir_parts, extract_data=fa_ir_parts_extract_data_from_html,
    #            write_data=fa_ir_parts_write_data_to_md,
    #            template_path="scripts/templates/fa_IR/parts/parts_template.md", dry_run=False)
    html_to_md(m.fa_ir_scientists, extract_data=fa_ir_scientists_extract_data_from_html,
               write_data=fa_ir_scientists_write_data_to_md,
               template_path="scripts/templates/fa_IR/scientists/scientists_template.md", dry_run=False)
    pass
