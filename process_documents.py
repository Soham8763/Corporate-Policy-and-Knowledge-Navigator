import os
import argparse
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data/documents"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    parser = argparse.ArgumentParser(description="Ingest a PDF file into the ChromaDB vector store.")
    parser.add_argument("--file", required=True, help="Path to the PDF file to ingest.")
    args = parser.parse_args()

    print("Starting data ingestion process...")
    documents = load_documents(args.file)
    if documents:
        chunks = split_documents(documents)
        save_to_chroma(chunks)
        print("Data ingestion complete.")

def load_documents(file_path):
    print(f"Loading document from {file_path}...")
    if not os.path.exists(file_path):
        print(f"Error: The file at {file_path} does not exist.")
        return None

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Add metadata for citing sources
    for doc in documents:
        doc.metadata['source'] = os.path.basename(file_path)

    print(f"Loaded {len(documents)} pages from {file_path}.")
    return documents

def split_documents(documents):
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks):
    print("Loading embedding model and saving to ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL)

    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        db.add_documents(chunks)
        print(f"Added {len(chunks)} chunks to existing database in {CHROMA_PATH}.")
    else:
        db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
        print(f"Created new database with {len(chunks)} chunks in {CHROMA_PATH}.")

if __name__ == "__main__":
    main()