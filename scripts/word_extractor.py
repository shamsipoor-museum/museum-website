import sys
import zipfile
import xml
from os import path as osp


WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
TABLE = WORD_NAMESPACE + 'tbl'
ROW = WORD_NAMESPACE + 'tr'
CELL = WORD_NAMESPACE + 'tc'


def open_word(path: str, xml_path: str = "word/document.xml"):
    with zipfile.ZipFile(path) as docx:
        return xml.etree.ElementTree.XML(docx.read(xml_path))


def read_table(tree):
    for table in tree.iter(TABLE):
        for row in table.iter(ROW):
            for cell in row.iter(CELL):
                print(''.join(node.text for node in cell.iter(TEXT)))


def write_pic(path: str, pic):
    with open(path, "wb") as pic_file:
        pic_file.write(pic)


def main():
    src = sys.argv[1]  # if sys.argv[1] else ""
    dst = sys.argv[2]  # if sys.argv[2] else ""
    verbosity = "--verbose" in sys.argv

    xml_tree = open_word(src)


if __name__ == "__main__":
    main()
