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
# from os import path as osp
from typing import Optional

# import pdfquery as pq
import fitz


def fitz_write_text(path: str, whole_text: list):
    with open(path, "wb") as dst:
        for page_text in whole_text:
            dst.write(page_text)
            # dst.write(bytes((12)))  # write page delimiter (form feed 0x0C)


def write_pic(path: str, pic):
    with open(path, "wb") as pic_file:
        pic_file.write(pic)


def fitz_write_image(doc, path: str, img):
    xref = img[0]  # get the XREF of the image
    pix = fitz.Pixmap(doc, xref)  # create a Pixmap

    if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
        pix = fitz.Pixmap(fitz.csRGB, pix)

    pix.save(path)  # save the image as png


# def pdf_to_xml(src: str, dst: str, encoding: str = "utf-8"):
#     pdf = pq.PDFQuery(src)
#     pdf.load()
#     pdf.tree.write(dst, pretty_print=True, encoding=encoding)


def main(src: Optional[str] = None, dst: Optional[str] = None):
    src = src if src is not None else sys.argv[1]
    dst = dst if dst is not None else sys.argv[2]
    verbosity = "--verbose" in sys.argv
    # pdf_to_xml(src, dst)

    # pdf = pq.PDFQuery(src)
    # pdf.load()
    # extracted_data = pdf.extract([("part_pic", "LTImage")])

    pdf = fitz.open(src, filetype="pdf")
    # whole_text = []
    whole_images = []
    for page_index in range(len(pdf)):
        page = pdf[page_index]

        image_list = page.get_images()

        if verbosity:
            if image_list:
                print(f"Found {len(image_list)} images on page {page_index+1}")
            else:
                print("No images found on page", page_index+1)

        print(len(image_list), image_list)
        whole_images.append(image_list[-1])
        # for image_index, img in enumerate(image_list, start=1):
        #     fitz_write_image(pdf, osp.join(dst, f"page_{page_index+1}-image_{image_index}.png"), img)

        # page_text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
        # whole_text.append(page_text)
    # print(whole_images)
    fitz_write_image(pdf, dst, whole_images[0])
    # fitz_write_image(pdf, osp.join(dst, f"{osp.splitext(osp.basename(src))[0]}.png"), whole_images[0])
    # fitz_write_text(osp.join(dst, "whole_text.txt"), whole_text)
    # write_pic(dst, extracted_data["part_pic"])


if __name__ == "__main__":
    main()
