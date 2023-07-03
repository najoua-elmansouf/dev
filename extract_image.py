!pip install fitz 
!pip install PyMuPDF
import os
import pandas as pd
from PIL import Image
from io import BytesIO
import fitz
import io

file = 'Statistique.pdf'
print(file)

target_name = f"{file}"
print(target_name)

pdf_file = fitz.open(file)
    # print ("number of pages: %i" % doc.pageCount)

    # page1 = doc.load_page(0)
    # page1text = page1.get_text("text")
    # print(page1text)

for page_index in range(len(pdf_file)):

    # get the page itself
    page = pdf_file[page_index]
    image_list = page.get_images()

    # printing number of images found in this page
    if image_list:
        print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
    else:
        print("[!] No images found on page", page_index)
    for image_index, img in enumerate(page.get_images(), start=1):

        # get the XREF of the image
        xref = img[0]

        # extract the image bytes
        base_image = pdf_file.extract_image(xref)
        image_bytes = base_image["image"]

        # get the image extension
        #image_ext = base_image["ext"]

        # load it to PIL
        image = Image.open(io.BytesIO(image_bytes))

        # save it to local disk
        image.save(f"{target_name}_{page_index+1}_{image_index}.jpeg")