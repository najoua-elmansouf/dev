import pdfplumber
import pandas as pd
import tiktoken

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

def process_pdf(file_path):
    # Extract PDF document data
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

    # Tokenize the documents
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens_per_document = []
    for header, docs in grouped_documents.items():
        for i, doc_content in enumerate(docs, 1):
            doc_content_str = str(doc_content)
            tokens = enc.encode(doc_content_str)
            tokens_per_document.append((header, i, len(tokens)))

    # Create a DataFrame and convert to CSV
    df = pd.DataFrame()
    data = []
    for header, docs in grouped_documents.items():
        for i, doc_content in docs:
            tokens = enc.encode(doc_content)
            data.append({'Header': header, 'Document': doc_content, 'Tokens': len(tokens)})

    df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)

    return df

# Example usage:
# df = process_pdf('path/to/your/file.pdf')
# df.to_csv('output.csv', index=False)


