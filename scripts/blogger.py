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
import shutil as su
import re
from typing import Collection, Optional, Type, Callable, Iterable, List, Dict, Any

# from pprint import pprint
from attrs import asdict, define, frozen, make_class, Factory
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
import qrcode as qr

_NUKE_DST_PATH_PROMPT_FMT = """[generator] {sec}.rules.nuke_dst_path is set to \
True and we are about to COMPLETELY REMOVE the entire '{dst_path}' directory tree \n
Do you really want us to do it? \n
1. Yes, go on and remove the entire '{dst_path}' directory tree
2. No, Abort everything and exit now
3. No, keep the '{dst_path}' as it is and continue \n"""

MATCH_EVERYTHING = r".*"
MATCH_NOTHING = r"[^\w\W]"
MATCH_MD = r"(?i:^.*\.md$)"
MATCH_HTML = r"(?i:^.*\.html$)"
MATCH_CSS = r"(?i:^.*\.css$)"
MATCH_TTF = r"(?i:^.*\.ttf$)"  # TrueType Font
MATCH_WOFF = r"(?i:^.*\.woff$)"  # Web Open Font Format
MATCH_WOFF2 = r"(?i:^.*\.woff2$)"  # Web Open Font Format 2
MATCH_QR_PAGES = r"qr_codes_.+\.html"
CE = (r"index\.html", MATCH_QR_PAGES)

qr_row_type = List[str]
qr_table_type = List[qr_row_type]
qr_pages_type = List[qr_table_type]  # List[List[List[str]]]


# Recursion MUST be optional; in the root Sec all you want is to convert the
# home page and move the favicon and NOT RECURSING TO THE SUBSECS
@frozen
class Rules:
    nuke_dst_path: bool = False

    convert_selectors: Iterable[str] = (MATCH_MD, )
    convert_selected_data: bool = True
    recursive_convert: bool = True
    overwrite_when_moving_converted: bool = True

    copy_selectors: Iterable[str] = (MATCH_EVERYTHING, )
    copy_selected_data: bool = False
    recursive_copy: bool = True
    overwrite_when_copying: bool = False

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
    sub_secs: list = Factory(list)
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
    custom_data_writer: Optional[Callable[[Any, str, Template, Dict[str, Any]], None]] = None
    # dst_selectors: Iterable[str] = (MATCH_HTML, )  # selecting all files with ".html" extension
    rules: Rules = Rules()


    generate_index: bool = True
    custom_index_generator: Optional[Callable[[Any, Iterable[str]], None]] = None
    index_template_path: Optional[str] = None
    index_filename: str = "index.html"  # Is relative to output_path
    index_title: str = "Index"  # The title to show in the browser titlebar and on top of the index
    # a function to extract a single IndexRow
    index_extractor: Optional[Callable[[str, str], Any]] = None
    custom_index_writer: Optional[Callable[[Any, Template, Collection], None]] = None


    generate_qr: bool = True
    custom_qr_generator: Optional[Callable[[Any, Iterable[str], bool, Iterable[str], int, int, str, str, bool], None]] = None
    custom_qr_img_generator: Optional[Callable[[Any, Iterable[str], bool], None]] = None
    qr_dirname: str = "qr_codes"  # Is relative to output_path
    generate_qrpages: bool = True
    custom_qrpages_extractor: Optional[Callable[[Any, int, int, Iterable[str]], qr_pages_type]] = None
    qrpages_template_path: Optional[str] = None
    qrpages_dirname: str = "qr_codes/pages"  # Is relative to output_path
    custom_qr_table_writer: Optional[Callable[[Any, qr_table_type, Template, str, str, str], None]] = None


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


def _vpg(verbose: bool, prefix: str, sep: Optional[str] = " ", end: Optional[str] = "\n",
         file: Optional[str] = None, flush: bool = False):
    if not verbose:
        def vp(*values: object, sep: Optional[str] = sep, end: Optional[str] = end,
               file: Optional[str] = file, flush: bool = flush):
            return
        return vp

    print(prefix.center(60, "═"))

    def vp(*values: object, sep: Optional[str] = sep, end: Optional[str] = end,
           file: Optional[str] = file, flush: bool = flush):
        print(prefix, *values, sep=sep, end=end, file=file, flush=flush)
    return vp


def content_generator(sec: SecSpec, exceptions: Iterable[str] = CE,
                      verbose: bool = False, _nuke_warning: bool = True):
    if _nuke_warning and sec.rules.nuke_dst_path:
        _vpg(True, "[! WARNING !]")("'sec.rules.nuke_dst_path' is set to True "
              "and it seems like you are running 'content_generator' directly"
              "'content_generator' won't enforce that rule, consider running the"
              "'generator' instead")
    vp = _vpg(verbose, "[content_generator]")
    if sec.custom_data_generator is not None:
        vp("'sec.custom_data_generator' is not None, delegating content generation to it")
        return sec.custom_data_generator(sec, exceptions)
    exceptions = re_collection_compiler(exceptions)
    if sec.rules.convert_selected_data and not (sec.data_extractor or sec.dst_template_path):
        vp("WARNING: 'sec.rules.convert_selected_data' is True but one of "
           "'sec.data_extractor' or 'sec.dst_template_path' is not provided, "
           "convertion needs both of these values to be provided with "
           "appropriate types")
    convert = sec.rules.convert_selected_data and sec.data_extractor and sec.dst_template_path
    convert_selectors = re_collection_compiler(sec.rules.convert_selectors)
    if convert:
        template = Environment(
            loader=FileSystemLoader(osp.dirname(sec.dst_template_path)),
            autoescape=False  # select_autoescape()  # False because we may want to use arbitrary html code in md files
        ).get_template(osp.basename(sec.dst_template_path))
    copy = sec.rules.copy_selected_data
    copy_selectors = re_collection_compiler(sec.rules.copy_selectors)
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
                    vp(f"Converting '{osp.join(dirpath, f)}' to '{dst_f_path}'")
                    # Preparing directory structure if sec.dst_path is nuked
                    os.makedirs(osp.dirname(dst_f_path), exist_ok=True)
                    if sec.custom_data_writer:
                        vp("using 'custom_data_writer'")
                        sec.custom_data_writer(sec, dst_f_path, template, sec.data_extractor(dirpath, f).__dict__)
                    else:
                        with open(dst_f_path, mode="w") as dst_f:
                            dst_f.write(
                                template.render(
                                    sec.data_extractor(dirpath, f).__dict__
                                )
                            )
                    # If copy and overwrite are both True, the following code
                    # would overwrite the converted file; so we have to jump
                    # to the next iteration
                    continue
            # Move
            if copy and re_collection_searcher(copy_selectors, f):
                dst_f_exists = osp.exists(osp.join(sec.dst_path, f))
                if not dst_f_exists or (
                    dst_f_exists and sec.rules.overwrite_when_copying
                ):
                    # The dst of copy have to be sec.dst_path + relation of the
                    # dirpath to src_path in order to keep the directory
                    # structure (avoid flattening it)
                    sf = osp.join(dirpath, f)
                    df = osp.join(
                        osp.join(
                            sec.dst_path,
                            osp.relpath(dirpath, sec.src_path)
                        ),
                        f
                    )
                    vp(f"Copying '{sf}' to '{df}'")
                    # Preparing directory structure if sec.dst_path is nuked
                    os.makedirs(osp.dirname(df), exist_ok=True)
                    su.copy(
                        sf,
                        osp.abspath(df)
                    )
        if not sec.rules.recursive_convert:
            convert = False
        if not sec.rules.recursive_copy:
            copy = False


def index_generator(sec: SecSpec, exceptions: Iterable[str] = CE,
                    verbose: bool = False):
    if sec.custom_index_generator:
        return sec.custom_index_generator(sec, exceptions)
    exceptions = re_collection_compiler(exceptions)
    index = sec.generate_index
    if verbose and index and not sec.index_template_path:
        vp = _vpg("[index_generator]")
        vp("'sec.generate_index' is True but 'sec.index_template_path' is not "
           "provided, index generation without a template is not possible; "
           "thus skipping the index generation")
        return
    index_rows = []
    index_selectors = re_collection_compiler(sec.rules.index_selectors)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if index and (re_collection_searcher(index_selectors, f)
            and not re_collection_searcher(exceptions, f)):
                index_rows.append(sec.index_extractor(dirpath, f))
        if not sec.rules.recursive_index:
            index = False

    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.index_template_path)),
        autoescape=select_autoescape()
    ).get_template(osp.basename(sec.index_template_path))
    # Preparing directory structure if sec.dst_path is nuked if it has not
    # done already by 'content_generator' (like when if 'sec.data_extractor'
    # and 'sec.rules.copy_selected_data' are None)
    os.makedirs(sec.dst_path, exist_ok=True)
    if sec.custom_index_writer:
        sec.custom_index_writer(sec, template, index_rows)
    else:
        with open(osp.join(sec.dst_path, sec.index_filename), mode="w") as f:
            f.write(template.render(title=sec.index_title, index=index_rows))


def qr_imgs_generator(sec: SecSpec, exceptions: Iterable[str] = CE, verbose: bool = False):
    vp = _vpg(verbose, "[qr_imgs_generator]")
    if not sec.url_prefix:
        vp("'qr_imgs' is True but 'sec.url_prefix' is not provided; skipping "
           "QR Image generation")
        return
    exceptions = re_collection_compiler(exceptions)
    for dirpath, dirnames, filenames in os.walk(sec.dst_path):
        for f in filenames:
            if f.endswith(".html"):
                if re_collection_searcher(exceptions, f):
                    continue
                f = osp.splitext(f)[0]
                vp("Generating QR Image for", sec.url_prefix + f)
                qrcode = qr.make(sec.url_prefix + f)
                # Preparing directory structure if sec.dst_path is nuked
                qr_dirpath = osp.join(sec.dst_path, sec.qr_dirname)
                os.makedirs(qr_dirpath, exist_ok=True)
                # print("[!!!]", osp.join(osp.join(sec.output_path, sec.qr_dirname), f + ".png"))
                qrcode.save(osp.join(qr_dirpath, f + ".png"))


def qr_pages_extractor(sec: SecSpec, rows: int = 5, cols: int = 4,
                      #  qr_name_attribute: str = "header",
                       exceptions: Iterable[str] = (r"index\.png", )) -> qr_pages_type:
    # """if 'qr_name_attribute' is set to ""; the file basenames will be used
    # for each qr name in the tables, otherwise, the 'sec.data_extractor' will
    # be called on the src file to extract the DataSpec and 'qr_name_attribute'
    # of the resulting DataSpec will be used as qr names (to give a better name)"""
    exceptions = re_collection_compiler(exceptions)
    pages: qr_pages_type = []
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


def qr_table_writer(sec: SecSpec, table: qr_table_type, template: Template,
                    path: str, mode: str = "w", title: str = "QR Codes"):
    with open(path, mode=mode) as f:
        f.write(template.render(title=title, table=table, enumerate=enumerate, len=len))



def qr_pages_generator(
    sec: SecSpec,
    exceptions: Iterable[str] = CE,
    rows: int = 5,
    cols: int = 4,
    filename_fmt: str = "qr_codes_{i}.html",
    title_fmt: str = "QR Codes {i}",
    verbose: bool = True
):
    vp = _vpg(verbose, "[qr_pages_generator]")
    if not sec.qrpages_template_path:
        vp("'sec.qrpages_template_path' is not provided; skipping the QR "
           "Pages generation")
        return
    if sec.custom_qrpages_extractor:
        pages = sec.custom_qrpages_extractor(sec, rows, cols, exceptions)
        vp("Using 'sec.custom_qrpages_extractor'")
    else:
        pages = qr_pages_extractor(sec, rows, cols, exceptions)
    # print(qr_pages_rows, qr_pages_cols)
    # pprint(pages)

    template = Environment(
        loader=FileSystemLoader(osp.dirname(sec.qrpages_template_path)),
        autoescape=False  # select_autoescape()  # We want to preserve html tags (for specifying fonts, etc)
    ).get_template(osp.split(sec.qrpages_template_path)[1])
    for i, table in enumerate(pages, start=1):
        dst_path = osp.join(
            osp.join(sec.dst_path, sec.qrpages_dirname),
            filename_fmt.format(i=i)
        )
        vp("Writing QR Page: '{}'".format(dst_path))
        # Preparing directory structure if sec.dst_path is nuked
        os.makedirs(osp.dirname(dst_path), exist_ok=True)
        if sec.custom_qr_table_writer:
            sec.custom_qr_table_writer(sec, table, template, dst_path,
                                       title=title_fmt.format(i=i))
        else:
            qr_table_writer(sec, table, template, dst_path,
                            title=title_fmt.format(i=i))


def qr_generator(
    sec: SecSpec,
    qr_imgs: bool = True,
    qr_imgs_exceptions: Iterable[str] = CE,
    qr_pages: bool = True,
    qr_pages_exceptions: Iterable[str] = CE,
    qr_pages_rows: int = 5,
    qr_pages_cols: int = 4,
    qr_pages_filename_fmt: str = "qr_codes_{i}.html",
    qr_pages_title_fmt: str = "QR Codes {i}",
    verbose: bool = False,
):
    vp = _vpg(verbose, "[qr_generator]")
    if sec.custom_qr_generator:
        vp("Using 'sec.custom_qr_generator'")
        return sec.custom_qr_generator(
            sec,
            qr_imgs_exceptions,
            qr_pages,
            qr_pages_exceptions,
            qr_pages_rows,
            qr_pages_cols,
            qr_pages_filename_fmt,
            qr_pages_title_fmt,
            verbose
        )
    vp("Generating QR Images")
    if qr_imgs and sec.url_prefix:
        if sec.custom_qr_img_generator:
            vp("Using 'sec.custom_qr_img_generator'")
            sec.custom_qr_img_generator(sec, qr_imgs_exceptions, verbose)
        else:
            qr_imgs_generator(sec, qr_imgs_exceptions, verbose)
    vp("Generating QR Pages")
    if qr_pages:
        qr_pages_generator(
            sec,
            qr_pages_exceptions,
            qr_pages_rows,
            qr_pages_cols,
            qr_pages_filename_fmt,
            qr_pages_title_fmt,
            verbose
        )


def nuke_handler(sec: SecSpec):
    print(_NUKE_DST_PATH_PROMPT_FMT.format(sec=sec.name, dst_path=sec.dst_path))
    while True:
        confirm = input("Your answer [1/2/3] (2 is the default): ")
        if confirm in ("2", ""):
            print("Aborting and exiting...")
            exit()
        elif confirm == "3":
            break
        elif confirm == "1":
            print("Removing", sec.dst_path, "...")
            try:
                su.rmtree(sec.dst_path)
            except FileNotFoundError:
                pass
            break
        else:
            print("Invalid input, choose between 1, 2 or 3")


def generator(sec: SecSpec, content_exceptions: Iterable[str] = CE,
              index: bool = True, index_exceptions: Iterable[str] = CE,
              qr: bool = True, qr_imgs: bool = True, qr_imgs_exceptions: Iterable[str] = CE,
              qr_pages: bool = True, qr_pages_exceptions: Iterable[str] = CE,
              qr_pages_rows: int = 5, qr_pages_cols: int = 4,
              qr_pages_filename_fmt: str = "qr_codes_{i}.html",
              qr_pages_title_fmt: str = "QR Codes {i}", verbose: bool = False,
              args_pass_through: bool = True):
    vp = _vpg(verbose, "[generator]")
    vp("Beginning with section {} ({})".format(sec.name, sec.url_prefix))
    if sec.rules.nuke_dst_path:
        nuke_handler(sec)
    if sec.src_path is not None and sec.dst_path is not None:
        if sec.data_extractor is None:
            vp("'sec.data_extractor' is None, 'content_generator' will only"
               "copy data according to 'sec.rules' ({})".format(sec.rules))
        content_generator(sec, exceptions=content_exceptions, verbose=verbose, _nuke_warning=False)

        if index and sec.generate_index and sec.index_extractor is not None:
            vp("'sec.data_extractor' is provided; generating content")
            index_generator(sec, exceptions=index_exceptions, verbose=verbose)
        else:
            vp("'index' is False or 'sec.index_extractor' is None; skipping index generation")

        if qr and sec.generate_qr:
            vp("Generating QR Codes")
            qr_generator(sec, qr_imgs, qr_imgs_exceptions, qr_pages,
                               qr_pages_exceptions, qr_pages_rows, qr_pages_cols,
                               qr_pages_filename_fmt, qr_pages_title_fmt, verbose=verbose)
        else:
            vp("'qr' is False; skipping QR Codes generation")
    else:
        vp("One (or both) of 'sec.src_path' and 'sec.dst_path' is 'None'; "
           "skipping to the sub_specs if any")
    for s in sec.sub_secs:
        if args_pass_through:
            generator(s, content_exceptions=content_exceptions,
                      index=index, index_exceptions=index_exceptions,
                      qr=qr, qr_imgs_exceptions=qr_imgs_exceptions,
                      qr_pages=qr_pages, qr_pages_exceptions=qr_pages_exceptions,
                      qr_pages_rows=qr_pages_rows, qr_pages_cols=qr_pages_cols,
                      qr_pages_filename_fmt=qr_pages_filename_fmt,
                      qr_pages_title_fmt=qr_pages_title_fmt, verbose=verbose,
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
