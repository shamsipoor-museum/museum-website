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
from jinja2 import Environment, FileSystemLoader, select_autoescape
import qrcode as qr

MATCH_EVERYTHING = r".*"
MATCH_NOTHING = r"[^\w\W]"
MATCH_MD = r"(?i:^.*\.md$)"
MATCH_HTML = r"(?i:^.*\.html$)"
GE = (r"index\.html", r"qr_codes_.+\.html")

# INDEX_RULES_DONT_RECURSE = 0
# INDEX_RULES_RECURSE_AND_KEEP_ONE_FLAT_INDEXFILE = 1
# INDEX_RULES_RECURSE_AND_SHOW_AS_ONE_TREE_INDEXFILE = 2
# INDEX_RULES_RECURSE_AND_SHOW_AS_MULTIPLE_FLAT_INDEXFILES = 3
# INDEX_RULES_RECURSE_AND_SHOW_AS_MULTIPLE_TREE_INDEXFILES = 4


# Roadblocks to True nuke_dst_path:
# Exceptions in fa_IR/parts (Parts with persian text in header)
# Lack of non-recursive generation option (it's necessary for the root SecSpec (favicon and the main page))
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
    # function to extract data_specs from files of input_path directory and also responsible to enforce the Rules
    # takes a SecSpec and rules.convert_selectors as input and returns a Dict[path, DataSpec]
    # SHOULD BECOME Callable[[dirpath, f], DataSpec]] without the responsibility to enforce Rules
    # data_extractor: Optional[Callable[[Any, Iterable[str]], Dict[str, Any]]] = None  # DEPRECATED
    data_extractor: Optional[Callable[[str, str], Any]] = None

    dst_template_path: Optional[str] = None
    # function to take a SecSpec and Dict[path, DataSpec] and templates each DataSpec to 'src_template_path' and writes
    # the resulting file to corresponding path relative to 'dst_path'
    # SHOULD BECOME Callable[[Any, str, Dict[str, Any]], None]
    custom_data_writer: Optional[Callable[[Any, str, Dict[str, Any]], None]] = None
    # dst_selectors: Iterable[str] = (MATCH_HTML, )  # selecting all files with ".html" extension
    rules: Rules = Rules()

    # extract_data_from_md: Optional[Callable] = None  # DEPRECATED
    # extract_data_from_html: Optional[Callable] = None  # DEPRECATED
    # write_data_to_md: Optional[Callable] = None  # DEPRECATED
    # write_data_to_html: Optional[Callable] = None  # DEPRECATED


    generate_index: bool = True
    custom_index_generator: Optional[Callable[[Any, Iterable[str]], None]] = None
    index_template_path: Optional[str] = None
    index_filename: str = "index.html"  # Is relative to output_path
    index_title: str = "Index"  # The title to show in the browser titlebar and on top of the index
    # a function to extract a single IndexRow
    index_extractor: Optional[Callable[[str, str], Any]] = None
    custom_index_writer: Optional[Callable[[Any, Collection], None]] = None
    # index_rules: int = 0


    generate_qr: bool = True
    custom_qr_generator: Optional[Callable] = None
    custom_qr_img_generator: Optional[Callable] = None
    qr_dirname: str = "qr_codes"  # Is relative to output_path
    generate_qrpages: bool = True
    custom_qrpages_generator: Optional[Callable] = None
    qrpages_template_path: Optional[str] = None
    qrpages_dirname: str = "qr_codes/pages"  # IS relative to output_path


# def _generate_html(sec: SecSpec, exceptions: Iterable[str] = GE):  # DEPRECATED
#     # DEPRECATED
#     if sec.src_path is not None:
#         for dirpath, dirnames, filenames in os.walk(sec.src_path):
#             for f in filenames:
#                 if f.endswith(".md"):
#                     if f in exceptions:
#                         continue
#                     sec.write_data_to_html(sec.extract_data_from_md)  # pseudo code
#         for dirpath, dirnames, filenames in os.walk(sec.dst_path):
#             for f in filenames:
#                 if f.endswith(".html"):
#                     if f in exceptions:
#                         continue
#                     sec.index_writer(sec.index_extractor)
#     for s in sec.sub_specs:
#         _generate_html(s)


def compile_re_collection(iterable):
    # lazy approach with generator expression sucks and it will let
    # exceptional files to be generated for some reason
    # (search_re_collection does not seem to like it)
    return [re.compile(e) for e in iterable]


def search_re_collection(iterable, string):
    for p in iterable:
        if p.search(string) is not None:
            return True
    return False


def _generate_content(sec: SecSpec, exceptions: Iterable[str] = GE):
    """Just chaining two calls, passing 'sec.extract_data()' to 'sec.write_data()'"""
    if sec.src_path is not None:
        sec.custom_data_writer(sec, sec.data_extractor(sec, exceptions=exceptions))


def generate_content(sec: SecSpec, exceptions: Iterable[str] = GE):
    if sec.custom_data_generator:
        return sec.custom_data_generator(sec, exceptions)
    exceptions = compile_re_collection(exceptions)
    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.dst_template_path)),
        autoescape=False  # select_autoescape()  # False because we may want to use arbitrary html code in markdown files
    ).get_template(osp.basename(sec.dst_template_path))
    convert = sec.rules.convert_selected_data
    convert_selectors = compile_re_collection(sec.rules.convert_selectors)
    move = sec.rules.move_selected_data
    move_selectors = compile_re_collection(sec.rules.move_selectors)
    for dirpath, dirnames, filenames in os.walk(sec.src_path):
        for f in filenames:
            # Convert
            if convert and search_re_collection(convert_selectors, f):
                f_base, f_ext = osp.splitext(f)
                dst_f_path = osp.join(sec.dst_path, f_base + f_ext.replace(".md", ".html"))
                dst_f_exists = osp.exists(dst_f_path)
                if not search_re_collection(exceptions, f) and (not dst_f_exists or (
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
            if move and search_re_collection(move_selectors, f):
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


def _generate_index(sec: SecSpec, exceptions: Iterable[str] = GE):
    """Just chaining two calls, passing 'sec.extract_index()' to 'sec.write_index()'"""
    if sec.src_path is not None:
        sec.custom_index_writer(sec, sec.index_extractor(sec, exceptions=exceptions))


def generate_index(sec: SecSpec, exceptions: Iterable[str] = GE):
    if sec.custom_index_generator:
        return sec.custom_index_generator(sec, exceptions)
    exceptions = compile_re_collection(exceptions)
    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    ).get_template(osp.basename(sec.index_template_path))
    index = sec.generate_index
    index_rows = []
    index_selectors = compile_re_collection(sec.rules.index_selectors)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if index and (search_re_collection(index_selectors, f)
            and not search_re_collection(exceptions, f)):
                index_rows.append(sec.index_extractor(dirpath, f))
        if not sec.rules.recursive_index:
            index = False

    if sec.custom_index_writer:
        sec.custom_index_writer(sec, index_rows)
    else:
        with open(osp.join(sec.dst_path, sec.index_filename), mode="w") as f:
            f.write(template.render(title=sec.index_title, index=index_rows))


def generate_qr_imgs(sec: SecSpec, exceptions: Iterable[str] = GE, dry_run: bool = False):
    exceptions = compile_re_collection(exceptions)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if f.endswith(".html"):
                if search_re_collection(exceptions, f):
                    continue
                f = osp.splitext(f)[0]
                if dry_run:
                    print(sec.url_prefix + f)
                else:
                    qrcode = qr.make(sec.url_prefix + f)
                    # print("[!!!]", osp.join(osp.join(sec.output_path, sec.qr_dirname), f + ".png"))
                    qrcode.save(osp.join(osp.join(sec.dst_path, sec.qr_dirname), f + ".png"))


def extract_qr_table(sec: SecSpec, rows: int = 5, cols: int = 4,
                     exceptions: Iterable[str] = (r"index\.png", )) -> tuple:
    exceptions = compile_re_collection(exceptions)
    pages: List[List[List[str]]] = []
    for dirpath, dirnames, filenames in os.walk(osp.join(sec.dst_path, sec.qr_dirname)):
        for f in filenames:
            if f.endswith(".png"):
                if search_re_collection(exceptions, f):
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
                        table[-1].append(osp.splitext(osp.basename(f))[0])
    return tuple(pages)


def write_qr_table(data, template, path, mode="w", title="QR Codes"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, table=data, enumerate=enumerate, len=len))


def generate_qr_codes(sec: SecSpec, exceptions: Iterable[str] = GE,
                      qr_pages: bool = True, qr_pages_exceptions: Iterable[str] = GE,
                      qr_pages_rows: int = 5, qr_pages_cols: int = 4,
                      qr_pages_filename_fmt: str = "qr_codes_{i}.html",
                      qr_pages_title_fmt: str = "QR Codes {i}", dry_run: bool = False):
    env = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qrpages_template_path)),
        autoescape=select_autoescape()
    )
    template = env.get_template(osp.split(sec.qrpages_template_path)[1])

    generate_qr_imgs(sec, exceptions=exceptions, dry_run=dry_run)
    if qr_pages:
        pages = extract_qr_table(sec, rows=qr_pages_rows, cols=qr_pages_cols, exceptions=qr_pages_exceptions)
        # print(qr_pages_rows, qr_pages_cols)
        # pprint(pages)
        for i, table in enumerate(pages, start=1):
            write_qr_table(table, template,
                           osp.join(osp.join(sec.dst_path, sec.qrpages_dirname), qr_pages_filename_fmt.format(i=i)),
                           title=qr_pages_title_fmt.format(i=i))


def generate(sec: SecSpec, content_exceptions: Iterable[str] = GE,
             index: bool = True, index_exceptions: Iterable[str] = GE,
             qr: bool = True, qr_exceptions: Iterable[str] = GE,
             qr_pages: bool = True, qr_pages_exceptions: Iterable[str] = GE,
             qr_pages_rows: int = 5, qr_pages_cols: int = 4,
             qr_pages_filename_fmt: str = "qr_codes_{i}.html", qr_pages_title_fmt: str = "QR Codes {i}",
             args_pass_through: bool = True):
    if sec.src_path is not None:
        generate_content(sec, exceptions=content_exceptions)
        if index:
            generate_index(sec, exceptions=index_exceptions)
        if qr:
            generate_qr_codes(sec, qr_exceptions, qr_pages, qr_pages_exceptions,
                              qr_pages_rows, qr_pages_cols,
                              qr_pages_filename_fmt, qr_pages_title_fmt)
    for s in sec.sub_specs:
        if args_pass_through:
            generate(s, content_exceptions=content_exceptions,
                        index=index, index_exceptions=index_exceptions,
                        qr=qr, qr_exceptions=qr_exceptions,
                        qr_pages=qr_pages, qr_pages_exceptions=qr_pages_exceptions,
                        qr_pages_rows=qr_pages_rows, qr_pages_cols=qr_pages_cols,
                        qr_pages_filename_fmt=qr_pages_filename_fmt,
                        qr_pages_title_fmt=qr_pages_title_fmt,
                        args_pass_through=args_pass_through)
        else:
            generate(s)


def read_file(path: str):
    with open(path, "r") as f:
        return f.read()


def read_file_bytes(path: str):
    with open(path, "rb") as f:
        return f.read()


def main():
    print("This framework is not meant to be executed like a script!",
          "Please refer to the documentation on how to use this framework to",
          "generate static websites.", sep="\n")


if __name__ == "__main__":
    main()
