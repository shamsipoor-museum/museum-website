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


document_root = b.SecSpec(
    name="root",
    dst_path="docs",
    url_prefix=gv.PREFIX,
    sub_specs=[fair.root]
)


def main(src_dir: Optional[str] = None, dst_dir: Optional[str] = None):
    b.generator(
        fair.parts,
        content_exceptions=(
            r"index\.html", r"qr_codes_.+\.html", r"choke_987\.md",
            r"choke_7825-5\.md", r"crt_465_tester\(b&k\)\.md",
            r"miller_big_rf_trans\.md"
        ),
        qr_pages_rows=1,
        qr_pages_cols=4
    )

    b.generator(
        fair.scientists,
        qr_pages_rows=1,
        qr_pages_cols=4
    )


if __name__ == "__main__":
    main()
