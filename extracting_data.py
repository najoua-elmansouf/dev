import pdfplumber

##divide the content based on the headers
def divide_content_by_header(content):
    lines = content.split('\n')  # Split the content into lines

    documents = []
    current_document = []

    for line in lines:
        if line.strip():  # Skip empty lines
            current_document.append(line)
            if len(current_document) == 1:  # Check if it's the first line of a document
                if current_document != [line]:  # Check if it's not the first document
                    documents.append('\n'.join(current_document[:-1]))  # Add previous document
                    current_document = [line]  # Start new document with the current line

    if current_document:
        documents.append('\n'.join(current_document))

    return documents

##extract pdf doc data
with open('C:/Users/rita/Downloads/CoC_LegislativeGuide.pdf', 'rb') as file:    
    # pdfplumber
    pdf = pdfplumber.open(file)
    text = ''
    tables = []
    for page in pdf.pages:
        text += page.extract_text()
        page_tables = page.extract_tables()
        tables.extend(page_tables)
    pdf.close()

documents = divide_content_by_header(text)

# Print the divided documents
for i, doc in enumerate(documents, 1):
    print(f"Document {i}:\n{doc.strip()}\n")
