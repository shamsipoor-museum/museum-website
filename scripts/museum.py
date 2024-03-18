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
from pprint import pprint
from datetime import date
from typing import Optional, Union, Type, Callable, Tuple, Dict

from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import frontmatter as fm

import blogger as b
import global_values as gv
import fair


def generate_beautiful_qr_codes(sec: b.SecSpec, exceptions: Tuple[str, ...] = b.GE,
                                qr_pages: bool = True,
                                qr_pages_exceptions: Tuple[str, ...] = b.GE,
                                qr_pages_rows: int = 5, qr_pages_cols: int = 4,
                                qr_pages_filename_fmt: str = "qr_codes_{i}.html",
                                qr_pages_title_fmt: str = "QR Codes {i}",
                                dry_run: bool = False):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qrpages_template_path)),
        autoescape=False  # select_autoescape()
    )
    template = env.get_template(osp.split(sec.qrpages_template_path)[1])

    b.generate_qr_imgs(sec, exceptions=exceptions, dry_run=dry_run)
    if qr_pages:
        pages = b.extract_qr_table(sec, rows=qr_pages_rows, cols=qr_pages_cols, exceptions=qr_pages_exceptions)
        # print(qr_pages_rows, qr_pages_cols)
        # pprint(pages)
        for i, table in enumerate(pages, start=1):
            # pprint(f'{sec.input_path = }; {table}; {[p + ".md" for p in table[0]]}')
            pprint(
                [
                    table,
                    [
                        sec.data_extractor(
                            dirpath=sec.src_path,
                            f=p + ".md"
                        ).header
                        for p in table[0]
                    ]
                ])
            b.write_qr_table(
                [
                    table,
                    [
                        sec.data_extractor(
                            dirpath=sec.src_path,
                            f=p + ".md"
                        ).header
                        for p in table[0]
                    ]
                ],
                template,
                osp.join(osp.join(sec.dst_path, sec.qrpages_dirname),
                         qr_pages_filename_fmt.format(i=i)),
                title=qr_pages_title_fmt.format(i=i)
            )


document_root = b.SecSpec(
    name="root",
    dst_path="docs",
    url_prefix=gv.PREFIX,
    sub_specs=[fair.root]
)


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    # b.generate_index(fair.parts, exceptions=b.GE)
    b.generate(fair.parts, content_exceptions=(
        r"index\.html", r"qr_codes_.+\.html", r"choke_987\.md",
        r"choke_7825-5\.md", r"crt_465_tester\(b&k\)\.md", r"miller_big_rf_trans\.md"
    ), qr_pages=False)
    generate_beautiful_qr_codes(fair.parts, exceptions=b.GE,
                                qr_pages_exceptions=b.GE,
                                qr_pages_rows=1, qr_pages_cols=4)

    # b.generate_index(fair.scientists, exceptions=b.GE)
    # b.generate(fair.scientists)
    b.generate(fair.scientists, qr_pages=False)
    generate_beautiful_qr_codes(fair.scientists, exceptions=b.GE,
                                qr_pages_exceptions=b.GE,
                                qr_pages_rows=1, qr_pages_cols=4)


if __name__ == "__main__":
    main()
