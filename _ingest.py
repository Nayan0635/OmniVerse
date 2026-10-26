import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

from loaders import load_file
from core import embedder, vector_store


def ingest(path: str):
    print(f"Loading {path} ...")
    text = load_file(path)
    print(f"   Extracted {len(text)} characters.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_text(text)
    print(f"   Split into {len(chunks)} chunks.")

    print("   Embedding chunks ...")
    embeddings = [embedder.embed(chunk) for chunk in chunks]

    source = os.path.basename(path)
    ids       = [f"{source}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]

    # delete old chunks of this source, then upsert fresh ones
    vector_store.delete_source(source)
    vector_store.upsert_chunks(ids, embeddings, chunks, metadatas)

    print(f"✅ Stored {len(chunks)} chunks from '{source}' in chromaDB")


if __name__ == "__main__":
    while True:
        path = input("\nEnter file path (or 'exit' to quit): ").strip()
        if path.lower() == "exit":
            print("Bye 👋")
            break
        if not path:
            print("❌ No path given.")
            continue
        try:
            ingest(path)
        except Exception as e:
            print(f"❌ Failed: {e}")


# documents/data.txt
# documents/mission_Titan.pdf
# documents/retail_sales.xlsx
# documents/space_missions.csv
# documents/urban_gardening.docx

