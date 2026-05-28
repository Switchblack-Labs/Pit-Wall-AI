from pathlib import Path

import fitz

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


DOCUMENTS_DIR = Path("app/rag/documents")


def extract_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def load_documents():

    documents = []

    pdf_files = DOCUMENTS_DIR.glob("*.pdf")

    for pdf_file in pdf_files:

        text = extract_pdf_text(pdf_file)

        document = Document(
            page_content=text,
            metadata={
                "source": pdf_file.name
            }
        )

        documents.append(document)

    return documents


def create_chunks(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    return chunks


if __name__ == "__main__":

    docs = load_documents()

    chunks = create_chunks(docs)

    print(f"{len(chunks)} chunks created")

    print(chunks[0].page_content[:500])