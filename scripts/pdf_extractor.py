import sys
from os import path as osp

import pdfquery as pq
import fitz

sdfdfd= ()


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


def pdf_to_xml(src: str, dst: str, encoding: str = "utf-8"):
    pdf = pq.PDFQuery(src)
    pdf.load()
    pdf.tree.write(dst, pretty_print=True, encoding=encoding)


def main():
    src = sys.argv[1]  # if sys.argv[1] else ""
    dst = sys.argv[2]  # if sys.argv[2] else ""
    verbosity = "--verbose" in sys.argv
    # pdf_to_xml(src, dst)

    # pdf = pq.PDFQuery(src)
    # pdf.load()
    # extracted_data = pdf.extract([("part_pic", "LTImage")])

    pdf = fitz.open(src, filetype="pdf")
    whole_text = []
    for page_index in range(len(pdf)):
        page = pdf[page_index]

        image_list = page.get_images()

        if verbosity:
            if image_list:
                print(f"Found {len(image_list)} images on page {page_index+1}")
            else:
                print("No images found on page", page_index+1)

        for image_index, img in enumerate(image_list, start=1):
            fitz_write_image(pdf, osp.join(dst, f"page_{page_index+1}-image_{image_index}.png"), img)

        page_text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
        whole_text.append(page_text)
    fitz_write_text(osp.join(dst, "whole_text.txt"), whole_text)
    # write_pic(dst, extracted_data["part_pic"])


if __name__ == "__main__":
    main()
