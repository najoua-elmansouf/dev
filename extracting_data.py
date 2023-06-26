import pdfplumber
import pandas as pd

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
file_path = ''

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

##Calculer les tokens
import tiktoken

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens_per_document = []
#summarizer = pipeline("summarization")

for header, docs in grouped_documents.items():
    for i, doc_content in enumerate(docs, 1):
        doc_content_str = str(doc_content)  
        tokens = enc.encode(doc_content_str)
        """
        if len(tokens) > 8191:
            # Load the pre-trained T5 model and tokenizer
            model_name = "t5-base"
            tokenizer = T5Tokenizer.from_pretrained(model_name)
            model = T5ForConditionalGeneration.from_pretrained(model_name)
            # Tokenize the input document
            inputs = tokenizer.encode("summarize: " + doc_content_str, return_tensors="pt")
            # Generate abstractive summary
            outputs = model.generate(inputs, max_length=100, num_beams=4, early_stopping=True)
            # Decode the generated summary
            summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Replace the document with its summary
            grouped_documents[header][i-1] = (i, summary)
            tokens = enc.encode(str(summary))"""
        tokens_per_document.append((header, i, len(tokens)))
            
"""
# Print the number of tokens in each document
for header, doc_num, tokens in tokens_per_document:
    print(f"Header: {header}")
    print(f"Document {doc_num}: {tokens} tokens\n")"""

#create a data frame and convert to csv
df = pd.DataFrame()
data = []

for header, docs in grouped_documents.items():
    for i, doc_content in docs:
        tokens = enc.encode(doc_content)
        data.append({'Header': header, 'Document': doc_content, 'Tokens': len(tokens)})

df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)

# Write to CSV
##df.to_csv('', index=False)

