from langchain_community.document_loaders import DirectoryLoader , TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
load_dotenv()

# Check if OpenAI API key is properly set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please add your API key to the .env file.")

DATA_PATH = "data"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

documents = load_documents()
chunks = text_splitter.split_documents(documents)

print(f"Loaded {len(documents)} documents and split into {len(chunks)} chunks")



#embeddings = OpenAIEmbeddings()
embeddings = OllamaEmbeddings(model="llama3.2")
vector_store = FAISS.from_documents(chunks, embeddings)

retriever = vector_store.as_retriever()

prompt = ChatPromptTemplate.from_messages([
    ("system", "ใช้ข้อมูลจากเอกสารในการตอบคำถามต่อไปนี้ให้สั้นกระชับและเข้าใจง่ายด้วยความสุภาพเป็นกันเอง"),
    ("user", "คำถาม:{question},ข้อมูลจากเอกสาร:{context}"),
])
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
question = "หัวเฉียวก่อตั้งเมื่อไร"
rag_chain = chain.invoke(question)

print(rag_chain)


