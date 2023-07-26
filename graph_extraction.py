import os
import PyPDF2

pdf_file_path = "C:/Users/rita/Downloads/cdgdev.pdf"
output_directory = "C:/Users/rita/Downloads"  # Specify the directory to save the extracted images

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

with open(pdf_file_path, "rb") as file:
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)

    for page_number in range(num_pages):
        page = pdf_reader.pages[page_number]
        if "/XObject" in page["/Resources"]:
            x_object = page["/Resources"]["/XObject"].get_object()
            for obj in x_object:
                if x_object[obj]["/Subtype"] == "/Image":
                    image = x_object[obj]
                    image_data = image._data  # Get the raw image data


                    objname = obj.replace("/", "")


                    image_path = os.path.join(output_directory, f"image{page_number}{objname}.png")
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_data)


                    print(f"Image saved: {image_path}")