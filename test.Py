import pandas as pd
import openai
import numpy as np
import tiktoken
import os
import pdfplumber


MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
ENCODING = "gpt2"
COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Read the OpenAI API key from an environment variable
openai.api_key ='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'
encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))
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

def get_embedding(text: str, model: str) -> list[float]:
    result = openai.Embedding.create(model=model, input=text)
    return result["data"][0]["embedding"]

def compute_doc_embeddings(df: pd.DataFrame, model: str) -> dict[tuple[str, str], list[float]]:
    return {idx: get_embedding(r.Document, model) for idx, r in df.iterrows()}

def vector_similarity(x: list[float], y: list[float]) -> float:
    return np.dot(np.array(x), np.array(y))

def order_by_similarity(query: str, contexts: dict[(str, str), np.array]) -> list[(float, (str, str))]:
    query_embedding = get_embedding(query, EMBEDDING_MODEL)
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    return document_similarities

def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame) -> tuple[list[str], int]:
    most_relevant_document_sections = order_by_similarity(question, context_embeddings)
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []
     
    for _, section_index in most_relevant_document_sections:
        document_section = df.loc[section_index]
        chosen_sections_len += document_section.Tokens + len(encoding.encode(SEPARATOR))
        if chosen_sections_len > MAX_SECTION_LEN:
            break
        chosen_sections.append(SEPARATOR + document_section.Document.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
        
    return chosen_sections, chosen_sections_len

def answer_with_gpt_4(query: str, df: pd.DataFrame, document_embeddings: dict, show_prompt: bool = False) -> tuple[str, int]:
    messages = [{"role": "system", "content": "Tu es un GDPR chatbot, réponds selon le contexte donné. Si tu n'es pas capable de répondre suivant le contexte , réponds de façon normale"}]
    prompt, section_length = construct_prompt(query, document_embeddings, df)
    if show_prompt:
        print(prompt)

    context = ""
    for article in prompt:
        context += article

    context += '\n\n --- \n\n + ' + query

    messages.append({"role": "user", "content": context})
    response = openai.ChatCompletion.create(model=COMPLETIONS_MODEL, messages=messages)

    return '\n' + response['choices'][0]['message']['content'], section_length

df = process_pdf("C:/Users/HP/Downloads/java2.pdf")

# Calculer les embeddings des documents
document_embeddings = compute_doc_embeddings(df, EMBEDDING_MODEL)

# Votre question
prompt = "c'est quoi java ?"

# Obtenir la réponse du modèle
response, sections_tokens = answer_with_gpt_4(prompt, df, document_embeddings)

# Afficher la réponse
print("Question:", prompt)
print("Réponse:", response)
print("Nombre total de tokens dans la réponse:", sections_tokens)
