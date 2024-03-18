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


def html_to_md(sec: b.SecSpec, exceptions: Optional[Tuple[str]] = b.GE,
               dry_run: bool = True):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.src_template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.basename(sec.src_template_path))

    exceptions = b.compile_re_collection(exceptions)
    # data_dict = dict()
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if f.endswith(".html"):
                if b.search_re_collection(exceptions, f):
                    continue
                extracted_data = sec.extract_data_from_html(dirpath, f)
                if dry_run:
                    print(dirpath, f, f.replace(".html", ".md"), sep=" --- ")
                    print(extracted_data)
                    print("---")
                else:
                    sec.write_data_to_md(extracted_data, template,
                                         osp.join(sec.src_path, f.replace(".html", ".md")))


# def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None,
#          template_path: Optional[str] = None, dry_run: bool = True):
#     src_dir = src_dir if src_dir is not None else sys.argv[1]
#     dst_dir = dst_dir if dst_dir is not None else sys.argv[2]
#     template_path = template_path if template_path is not None else sys.argv[2]
#     env = Environment(
#         loader=FileSystemLoader(osp.dirname(template_path)),
#         autoescape=False  # select_autoescape()
#     )
#     template = env.get_template("parts_template.md")


if __name__ == "__main__":
    # main(src_dir=m.fa_ir_parts.output_path, dst_dir=m.fa_ir_parts.input_path,
    #      template_path=m.fa_ir_parts.md_template_path)
    # html_to_md(m.fa_ir_parts, dry_run=False)
    # html_to_md(m.fa_ir_scientists, dry_run=False)
    pass
