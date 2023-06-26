import pandas as pd
import openai
import numpy as np

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

print(order_by_similarity("quel est l ordre du jour", document_embeddings)[:5])

