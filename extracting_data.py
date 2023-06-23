import pdfplumber

def divide_content_by_header(content):
    lines = content.split('\n')  # Split the content into lines

    documents = {}
    current_header = None

    for line in lines:
        if line.strip():  # Skip empty lines
            if current_header is None:  # Set the current header
                current_header = line
                documents[current_header] = ''
            elif line == current_header:  # Found a new header
                current_header = line
                documents[current_header] = ''
            else:
                documents[current_header] += line + '\n'  # Add line to the current header

    return documents

# Extract PDF document data
file_path = 'path'

documents = []
with pdfplumber.open(file_path) as pdf:
    for i, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        documents.append((i, text.strip()))

# Sort the documents based on page number
documents.sort(key=lambda x: x[0])

# Divide content by headers for each page
divided_documents = []
for i, content in documents:
    divided = divide_content_by_header(content)
    divided_documents.append((i, divided))

# Regroup documents with the same header
grouped_documents = {}
for i, doc in divided_documents:
    for header, content in doc.items():
        if header not in grouped_documents:
            grouped_documents[header] = []
        grouped_documents[header].append((i, content))

# Print the grouped documents
for header, docs in grouped_documents.items():
    print(f"Header: {header}\n")
    for i, doc_content in docs:
        print(f"Document {i}:\n{doc_content.strip()}\n")
