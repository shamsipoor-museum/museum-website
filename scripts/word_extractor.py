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
import zipfile
# import xml
from xml.etree import ElementTree
from xml.dom import minidom
# from os import path as osp


WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
TABLE = WORD_NAMESPACE + 'tbl'
ROW = WORD_NAMESPACE + 'tr'
CELL = WORD_NAMESPACE + 'tc'


def open_word(path: str, xml_path: str = "word/document.xml"):
    with zipfile.ZipFile(path) as docx:
        return ElementTree.XML(docx.read(xml_path))


def extract_table(tree):
    table_data = []
    for table in tree.iter(TABLE):
        for row in table.iter(ROW):
            for cell in row.iter(CELL):
                # print(''.join(node.text for node in cell.iter(TEXT)))
                for node in cell.iter(TEXT):
                    table_data.append(node.text)
    return table_data


def extract_text(tree, join_texts_in_paragraphs: bool = True):
    whole_text = []
    for paragraph in tree.iter(PARA):
        paragraph_text = []
        for node in paragraph.iter(TEXT):
            paragraph_text.append(node.text)
        paragraph_text = paragraph_text if not join_texts_in_paragraphs else "".join(paragraph_text)
        whole_text.append(paragraph_text)
    return whole_text


def write_pic(path: str, pic):
    with open(path, "wb") as pic_file:
        pic_file.write(pic)


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def main():
    src = sys.argv[1]  # if sys.argv[1] else ""
    # dst = sys.argv[2]  # if sys.argv[2] else ""
    # verbosity = "--verbose" in sys.argv

    xml_tree = open_word(src)
    # print(prettify(xml_tree))
    # explanation_paragrahs = "".join(extract_text(xml_tree)[21:])
    # for t in extract_text(xml_tree)[21:][:-1]:
    #     print(t)
    explanation_index = extract_text(xml_tree).index('توضیحات:') + 1
    print(extract_text(xml_tree)[explanation_index:][:-1])
    # print(explanation_paragrahs)


if __name__ == "__main__":
    main()
