import pandas as pd
import openai
import numpy as np
import tiktoken
import os

MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
ENCODING = "gpt2"
COMPLETIONS_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"

# Read the OpenAI API key from an environment variable
<<<<<<< HEAD
openai.api_key = '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'
=======
openai.api_key = ''
>>>>>>> fb30ec778057f51551e06611765192e676938c01
encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

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

def main():
    # Replace this line with the code to load your DataFrame
    # For demonstration purposes, let's create a sample DataFrame df
    data = {
        'Header': ['Header 1', 'Header 2'],
        'Document': ['Sample document 1', 'Sample document 2'],
        'Tokens': [100, 200]
    }
    df = pd.DataFrame(data)

    document_embeddings = compute_doc_embeddings(df, EMBEDDING_MODEL)
    prompt = "capitale france  "
    response, sections_tokens = answer_with_gpt_4(prompt, df, document_embeddings)
    print(response)

if __name__ == "__main__":
    main()
