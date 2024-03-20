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
import shutil as su
import re
from typing import Collection, Optional, Union, Type, Callable, Iterable, List, Dict, Any

# from pprint import pprint
from attrs import asdict, define, frozen, make_class, Factory
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import qrcode as qr

MATCH_EVERYTHING = r".*"
MATCH_NOTHING = r"[^\w\W]"
MATCH_MD = r"(?i:^.*\.md$)"
MATCH_HTML = r"(?i:^.*\.html$)"
GE = (r"index\.html", r"qr_codes_.+\.html")


# Roadblocks to True nuke_dst_path:
# Exceptions in fa_IR/parts (Parts with persian text in header)

# Recursion MUST be optional; in the root Sec all you want is to convert the
# home page and move the favicon and NOT RECURSING TO THE SUBSECS
@frozen
class Rules:
    nuke_dst_path: bool = False

    convert_selectors: Iterable[str] = (MATCH_MD, )
    convert_selected_data: bool = True
    recursive_convert: bool = True
    overwrite_when_moving_converted: bool = True

    move_selectors: Iterable[str] = (MATCH_EVERYTHING, )
    move_selected_data: bool = False
    recursive_move: bool = True
    overwrite_when_moving: bool = False

    index_selectors: Iterable[str] = (MATCH_HTML, )
    # There is no 'index_selected_data'; you should use 'generate_index'
    # directly when instantiating the SecSpec
    recursive_index: bool = True
    onefile_index: bool = True
    trees_in_index: bool = False  # False means flat index


@define
class SecSpec:
    name: str
    dst_path: str
    url_prefix: Optional[str] = None
    src_path: Optional[str] = None
    sub_specs: list = Factory(list)
    data_spec: Optional[Type] = None

    src_template_path: Optional[str] = None
    custom_data_generator: Optional[Callable[[Any, Iterable[str]], None]] = None
    # function to take 'dirpath' and 'f' and extract a single data_spec from
    # that file; 'data_generator' will enforce the 'rules'; thus
    # 'data_extractor' does not have anything to do with the 'rules'
    data_extractor: Optional[Callable[[str, str], Any]] = None

    dst_template_path: Optional[str] = None
    # function to take a SecSpec, a filename relative to 'dst_path' and
    # Dict[str, Any] (data_spec.__dict__), templates the DataSpec dict to
    # 'src_template_path' and writes the resulting file to the filename
    # relative to 'dst_path'
    custom_data_writer: Optional[Callable[[Any, str, Dict[str, Any]], None]] = None
    # dst_selectors: Iterable[str] = (MATCH_HTML, )  # selecting all files with ".html" extension
    rules: Rules = Rules()


    generate_index: bool = True
    custom_index_generator: Optional[Callable[[Any, Iterable[str]], None]] = None
    index_template_path: Optional[str] = None
    index_filename: str = "index.html"  # Is relative to output_path
    index_title: str = "Index"  # The title to show in the browser titlebar and on top of the index
    # a function to extract a single IndexRow
    index_extractor: Optional[Callable[[str, str], Any]] = None
    custom_index_writer: Optional[Callable[[Any, Collection], None]] = None


    generate_qr: bool = True
    custom_qr_generator: Optional[Callable[[Any, Iterable[str], bool, Iterable[str], int, int, str, str, bool], None]] = None
    custom_qr_img_generator: Optional[Callable[[Any, Iterable[str], bool], None]] = None
    qr_dirname: str = "qr_codes"  # Is relative to output_path
    generate_qrpages: bool = True
    custom_qrpages_generator: Optional[Callable[[Any, int, int, Iterable[str]], List[List[List[str]]]]] = None
    qrpages_template_path: Optional[str] = None
    qrpages_dirname: str = "qr_codes/pages"  # Is relative to output_path
    custom_qr_table_writer: Optional[Callable[[Any, List[List[str]], Template, str, str, str], None]] = None


def re_collection_compiler(iterable):
    # lazy (generator expression) approach does not work and lets
    # exceptional files to be generated for some reason
    # (search_re_collection does not seem to like it)
    return [re.compile(e) for e in iterable]


def re_collection_searcher(iterable, string):
    for p in iterable:
        if p.search(string) is not None:
            return True
    return False


def content_generator(sec: SecSpec, exceptions: Iterable[str] = GE):
    if sec.custom_data_generator:
        return sec.custom_data_generator(sec, exceptions)
    exceptions = re_collection_compiler(exceptions)
    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.dst_template_path)),
        autoescape=False  # select_autoescape()  # False because we may want to use arbitrary html code in markdown files
    ).get_template(osp.basename(sec.dst_template_path))
    convert = sec.rules.convert_selected_data
    convert_selectors = re_collection_compiler(sec.rules.convert_selectors)
    move = sec.rules.move_selected_data
    move_selectors = re_collection_compiler(sec.rules.move_selectors)
    for dirpath, dirnames, filenames in os.walk(sec.src_path):
        for f in filenames:
            # Convert
            if convert and re_collection_searcher(convert_selectors, f):
                f_base, f_ext = osp.splitext(f)
                dst_f_path = osp.join(sec.dst_path, f_base + f_ext.replace(".md", ".html"))
                dst_f_exists = osp.exists(dst_f_path)
                if not re_collection_searcher(exceptions, f) and (not dst_f_exists or (
                    dst_f_exists and sec.rules.overwrite_when_moving_converted
                )):
                    if sec.custom_data_writer:
                        sec.custom_data_writer(sec, f, sec.data_extractor(dirpath, f).__dict__)
                    else:
                        with open(dst_f_path, mode="w") as dst_f:
                            dst_f.write(
                                template.render(
                                    sec.data_extractor(dirpath, f).__dict__
                                )
                            )
                    # If move and overwrite are both True, the following code
                    # would overwrite the converted file; so we have to jump
                    # to the next iteration
                    continue
            # Move
            if move and re_collection_searcher(move_selectors, f):
                dst_f_exists = osp.exists(osp.join(sec.dst_path, f))
                if not dst_f_exists or (
                    dst_f_exists and sec.rules.overwrite_when_moving
                ):
                    # with open(osp.join(sec.dst_path, f), mode="wb") as dst_f:
                    #     dst_f.write(read_file_bytes(osp.join(dirpath, f)))
                    su.copy(osp.join(dirpath, f), osp.join(sec.dst_path, f))
        if not sec.rules.recursive_convert:
            convert = False
        if not sec.rules.recursive_move:
            move = False


def index_generator(sec: SecSpec, exceptions: Iterable[str] = GE):
    if sec.custom_index_generator:
        return sec.custom_index_generator(sec, exceptions)
    exceptions = re_collection_compiler(exceptions)
    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    ).get_template(osp.basename(sec.index_template_path))
    index = sec.generate_index
    index_rows = []
    index_selectors = re_collection_compiler(sec.rules.index_selectors)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if index and (re_collection_searcher(index_selectors, f)
            and not re_collection_searcher(exceptions, f)):
                index_rows.append(sec.index_extractor(dirpath, f))
        if not sec.rules.recursive_index:
            index = False

    if sec.custom_index_writer:
        sec.custom_index_writer(sec, index_rows)
    else:
        with open(osp.join(sec.dst_path, sec.index_filename), mode="w") as f:
            f.write(template.render(title=sec.index_title, index=index_rows))


def qr_imgs_generator(sec: SecSpec, exceptions: Iterable[str] = GE, dry_run: bool = False):
    exceptions = re_collection_compiler(exceptions)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if f.endswith(".html"):
                if re_collection_searcher(exceptions, f):
                    continue
                f = osp.splitext(f)[0]
                if dry_run:
                    print(sec.url_prefix + f)
                else:
                    qrcode = qr.make(sec.url_prefix + f)
                    # print("[!!!]", osp.join(osp.join(sec.output_path, sec.qr_dirname), f + ".png"))
                    qrcode.save(osp.join(osp.join(sec.dst_path, sec.qr_dirname), f + ".png"))


def qr_pages_extractor(sec: SecSpec, rows: int = 5, cols: int = 4,
                      #  qr_name_attribute: str = "header",
                       exceptions: Iterable[str] = (r"index\.png", )) -> List[List[List[str]]]:
    # """if 'qr_name_attribute' is set to ""; the file basenames will be used
    # for each qr name in the tables, otherwise, the 'sec.data_extractor' will
    # be called on the src file to extract the DataSpec and 'qr_name_attribute'
    # of the resulting DataSpec will be used as qr names (to give a better name)"""
    exceptions = re_collection_compiler(exceptions)
    pages: List[List[List[str]]] = []
    for dirpath, dirnames, filenames in os.walk(osp.join(sec.dst_path, sec.qr_dirname)):
        for f in filenames:
            if f.endswith(".png"):
                if re_collection_searcher(exceptions, f):
                    continue
                if len(pages) == 0 or (len(pages[-1]) >= rows and len(pages[-1][-1]) >= cols):
                    pages.append([])
                table = pages[-1]
                # print("[$$$]", f, table)
                table_len = len(table)
                if table_len <= rows:
                    if (table_len == 0 or len(table[-1]) >= cols) and table_len + 1 <= rows:
                        table.append([])
                    if len(table[-1]) < cols:
                        qr_basename = osp.splitext(osp.basename(f))[0]
                        table[-1].append(qr_basename)
                        # if qr_name_attribute:
                        #     table[-1].append(
                        #         sec.data_extractor(
                        #             dirpath=sec.src_path,
                        #             f=qr_basename + ".md"
                        #         ).__dict__[qr_name_attribute]
                        #     )
    return pages


def qr_table_writer(sec: Any, table: List[List[str]], template: Template,
                    path: str, mode: str = "w", title: str = "QR Codes"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, table=table, enumerate=enumerate, len=len))


def qr_codes_generator(
    sec: SecSpec,
    qr_imgs: bool = True,
    qr_imgs_exceptions: Iterable[str] = GE,
    qr_pages: bool = True,
    qr_pages_exceptions: Iterable[str] = GE,
    qr_pages_rows: int = 5,
    qr_pages_cols: int = 4,
    qr_pages_filename_fmt: str = "qr_codes_{i}.html",
    qr_pages_title_fmt: str = "QR Codes {i}",
    dry_run: bool = False
):
    if sec.custom_qr_generator:
        return sec.custom_qr_generator(
            sec,
            qr_imgs_exceptions,
            qr_pages,
            qr_pages_exceptions,
            qr_pages_rows,
            qr_pages_cols,
            qr_pages_filename_fmt,
            qr_pages_title_fmt,
            dry_run
        )
    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qrpages_template_path)),
        autoescape=False  # select_autoescape()  # We want to preserve html tags (for specifying fonts, etc)
    ).get_template(osp.split(sec.qrpages_template_path)[1])

    if qr_imgs:
        if sec.custom_qr_img_generator:
            sec.custom_qr_img_generator(sec, qr_imgs_exceptions, dry_run)
        else:
            qr_imgs_generator(sec, qr_imgs_exceptions, dry_run)
    if qr_pages:
        if sec.custom_qrpages_generator:
            pages = sec.custom_qrpages_generator(
                sec,
                qr_pages_rows,
                qr_pages_cols,
                qr_pages_exceptions
            )
        else:
            pages = qr_pages_extractor(
                sec,
                qr_pages_rows,
                qr_pages_cols,
                qr_pages_exceptions
            )
        # print(qr_pages_rows, qr_pages_cols)
        # pprint(pages)
        for i, table in enumerate(pages, start=1):
            if sec.custom_qr_table_writer:
                sec.custom_qr_table_writer(
                    sec,
                    table,
                    template,
                    osp.join(
                        osp.join(sec.dst_path, sec.qrpages_dirname),
                        qr_pages_filename_fmt.format(i=i)
                    ),
                    title=qr_pages_title_fmt.format(i=i)
                )
            else:
                qr_table_writer(
                    sec,
                    table,
                    template,
                    osp.join(
                        osp.join(sec.dst_path, sec.qrpages_dirname),
                        qr_pages_filename_fmt.format(i=i)
                    ),
                    title=qr_pages_title_fmt.format(i=i)
                )


def generator(sec: SecSpec, content_exceptions: Iterable[str] = GE,
              index: bool = True, index_exceptions: Iterable[str] = GE,
              qr: bool = True, qr_imgs: bool = True, qr_imgs_exceptions: Iterable[str] = GE,
              qr_pages: bool = True, qr_pages_exceptions: Iterable[str] = GE,
              qr_pages_rows: int = 5, qr_pages_cols: int = 4,
              qr_pages_filename_fmt: str = "qr_codes_{i}.html",
              qr_pages_title_fmt: str = "QR Codes {i}",
              args_pass_through: bool = True):
    if sec.src_path is not None:
        content_generator(sec, exceptions=content_exceptions)
        if index:
            index_generator(sec, exceptions=index_exceptions)
        if qr:
            qr_codes_generator(sec, qr_imgs, qr_imgs_exceptions, qr_pages,
                               qr_pages_exceptions, qr_pages_rows, qr_pages_cols,
                               qr_pages_filename_fmt, qr_pages_title_fmt)
    for s in sec.sub_specs:
        if args_pass_through:
            generator(s, content_exceptions=content_exceptions,
                      index=index, index_exceptions=index_exceptions,
                      qr=qr, qr_imgs_exceptions=qr_imgs_exceptions,
                      qr_pages=qr_pages, qr_pages_exceptions=qr_pages_exceptions,
                      qr_pages_rows=qr_pages_rows, qr_pages_cols=qr_pages_cols,
                      qr_pages_filename_fmt=qr_pages_filename_fmt,
                      qr_pages_title_fmt=qr_pages_title_fmt,
                      args_pass_through=args_pass_through)
        else:
            generator(s)


def file_reader(path: str):
    with open(path, "r") as f:
        return f.read()


def bytes_file_reader(path: str):
    with open(path, "rb") as f:
        return f.read()


def main():
    print("This framework is not meant to be executed like a script!",
          "Please refer to the documentation on how to use this framework to",
          "generate static websites.", sep="\n")


if __name__ == "__main__":
    main()
