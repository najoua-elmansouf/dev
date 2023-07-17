import pandas as pd
import openai
import numpy as np
import tiktoken

MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
ENCODING = "gpt2"

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

df  = pd.read_csv('')
#print(df.head())
#df = df.set_index(["Header"])
"""print(f"{len(df)} rows in the data.")
print(df.head(1).to_markdown())"""

EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETIONS_MODEL = "gpt-3.5-turbo"
openai.api_key = ''


def get_embedding(text: str, model: str=EMBEDDING_MODEL) -> list[float]:
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]

def compute_doc_embeddings(df: pd.DataFrame) -> dict[tuple[str, str], list[float]]:
    
    #Create an embedding for each row in the dataframe using the OpenAI Embeddings API.
    
    #Return a dictionary that maps between each embedding vector and the index of the row that it corresponds to.
    
    return {
        idx: get_embedding(r.Document) for idx, r in df.iterrows()
    }

document_embeddings = compute_doc_embeddings(df)

# An example embedding:
example_entry = list(document_embeddings.items())[0]
#print(f"{example_entry[0]} : {example_entry[1][:5]}... ({len(example_entry[1])} entries)")


def vector_similarity(x: list[float], y: list[float]) -> float:
    
    return np.dot(np.array(x), np.array(y))

def order_by_similarity(query: str, contexts: dict[(str, str), np.array]) -> list[(float, (str, str))]:
   
    query_embedding = get_embedding(query)
    
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    
    return document_similarities

##print(order_by_similarity("quel est l ordre du jour", document_embeddings)[:5])


def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    
    most_relevant_document_sections = order_by_similarity(question, context_embeddings)
    
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []
     
    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.        
        document_section = df.loc[section_index]
        
        chosen_sections_len += document_section.Tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break
            
        chosen_sections.append(SEPARATOR + document_section.Document.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
            
        
    return chosen_sections, chosen_sections_len

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 2000,
    "model" : COMPLETIONS_MODEL }

def answer_with_gpt_4(
    query: str,
    df: pd.DataFrame,
    document_embeddings: dict[(str, str), np.array],
    show_prompt: bool = False
) -> str:
    messages = [
        {"role" : "system", "content":"Tu es un GDPR chatbot, réponds selon le contexte donné. Si tu n'es pas capable de répondre suivant le contexte , réponds de façon normale"}
    ]
    prompt, section_lenght = construct_prompt(
        query,
        document_embeddings,
        df
    )
    if show_prompt:
        print(prompt)

    context= ""
    for article in prompt:
        context = context + article 

    context = context + '\n\n --- \n\n + ' + query

    messages.append({"role" : "user", "content":context})
    response = openai.ChatCompletion.create(
        model=COMPLETIONS_MODEL,
        messages=messages
        )

    return '\n' + response['choices'][0]['message']['content'], section_lenght

prompt = "donne moi le resultat net du métier amenagement"
response, sections_tokens = answer_with_gpt_4(prompt, df, document_embeddings)
print(response)

