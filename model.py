import pdfplumber

with open('C:/Users/rita/Downloads/CoC_LegislativeGuide.pdf', 'rb') as file:    
    # pdfplumber
    pdf = pdfplumber.open(file)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    pdf.close()