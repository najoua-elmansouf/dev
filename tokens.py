import tiktoken

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens_per_document = []

for header, docs in grouped_documents.items():
    for i, doc_content in enumerate(docs, 1):
        doc_content_str = str(doc_content)  # Convert doc_content to string
        tokens = enc.encode(doc_content_str)
        tokens_per_document.append((header, i, len(tokens)))

# Print the number of tokens in each document
for header, doc_num, tokens in tokens_per_document:
    print(f"Header: {header}")
    print(f"Document {doc_num}: {tokens} tokens\n")
    