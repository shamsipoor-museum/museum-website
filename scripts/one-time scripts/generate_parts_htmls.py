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
from typing import Optional, Union

# from mako.template import Template
from attrs import frozen, asdict
from jinja2 import Environment, FileSystemLoader, select_autoescape

import pdf_extractor as pe
import word_extractor as we


@frozen
class PartData:
    part_title: str = ""
    part_name: str = ""
    part_pic: str = ""
    manufacturing_date: int = 0
    part_category: str = ""
    manufacturer_name: str = ""
    manufacturer_country: str = ""
    explanation_paragraphs: Union[str, tuple] = ("", "")


def extract_part_data(src,
                      extract_image_from_corresponding_pdf_to: Optional[str] = None,
                      explanation_indicator: str = 'توضیحات:'):
    xml_tree = we.open_word(src)
    table = ''.join(cell.strip() for cell in we.extract_table(xml_tree)).split(":")
    # for cell in table:
    #     print(cell)
    part_title = osp.splitext(osp.basename(src))[0].strip()
    pic_file = part_title.casefold().replace(" ", "_") + ".png"
    extracted_text = we.extract_text(xml_tree)
    explanation_index = extracted_text.index(explanation_indicator) + 1
    if extract_image_from_corresponding_pdf_to is not None:
        pdf_file = osp.splitext(src)[0] + ".pdf"
        try:
            pe.main(src=pdf_file, dst=osp.join(extract_image_from_corresponding_pdf_to, pic_file))
        except Exception:
            print("[!]", src, part_title)
    return PartData(part_title=part_title,
                    part_name=table[2][:-10],
                    part_pic=osp.join("pics", pic_file),
                    manufacturing_date=table[1][:4],
                    part_category=table[4][:-11],
                    manufacturer_name=table[3][:-9],
                    manufacturer_country=table[5],
                    explanation_paragraphs=tuple(we.extract_text(xml_tree)[explanation_index:][:-1])
                    )


def write_templated_part_data(pd, template, path, mode="w"):
    with open(path, mode) as f:
        f.write(template.render(asdict(pd)))


def main(src_dir: Optional[str] = None):
    src_dir = src_dir if src_dir is not None else sys.argv[1]
    containing_dir = osp.normpath(osp.join(__file__, os.pardir))
    # template = Template(filename=osp.join(containing_dir, "template.html"))
    # print(template.render(explanation_paragraphs=explanation_paragraphs))
    env = Environment(
        loader=FileSystemLoader(osp.join(containing_dir, "templates")),
        autoescape=select_autoescape()
    )
    template = env.get_template("parts_template.html")
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith(".docx"):
                pic_path = None
                if osp.exists(osp.join(dirpath, osp.splitext(f)[0] + ".pdf")):
                    # if corresponding pdf file exits
                    pic_path = "scripts/generated_content/pics"
                extracted_part_data = extract_part_data(
                    osp.join(dirpath, f),
                    pic_path
                )
                write_templated_part_data(
                    extracted_part_data,
                    template,
                    osp.join(
                        "scripts/generated_content",
                        extracted_part_data.part_title.casefold().replace(" ", "_") + ".html"
                    )
                )

        # print(dirpath, dirnames, filenames)
    # print(template.render(explanation_paragraphs=explanation_paragraphs))


if __name__ == "__main__":
    main(src_dir="scripts/original_content")
