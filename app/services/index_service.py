import os
from uuid import uuid4
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import UploadFile

load_dotenv()

def index_user_course_pdf(user_id: str, course_id: str, file: UploadFile):
    namespace = f"{user_id}-{course_id}"
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "upskill"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-central1")
        )
    index = pc.Index(index_name)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)

    temp_path = f"app/data/uploads/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    loader = PyPDFLoader(temp_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vectorstore.add_documents(documents=chunks)
    os.remove(temp_path)
    return {"message": f"Indexed PDF cho {user_id} - {course_id}"}