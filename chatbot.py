from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
import time
import sys
from langchain_ollama import OllamaEmbeddings

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # For Python versions without reconfigure
        pass

# Load environment variables
load_dotenv()

# Check if OpenAI API key is properly set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please add your API key to the .env file.")

DATA_PATH = "data"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents

def setup_rag_chain():
    print("กำลังโหลดข้อมูลและตั้งค่าระบบ...")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    documents = load_documents()
    chunks = text_splitter.split_documents(documents)

    print(f"โหลด {len(documents)} เอกสาร และแบ่งเป็น {len(chunks)} ชิ้นส่วน")

    # Create embeddings and vector store
    #embeddings = OpenAIEmbeddings()
    embeddings = OllamaEmbeddings(model="llama3.2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever()

    # Set up the conversation memory
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        input_key="question"
    )

    # Set up the prompt template with chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", "คุณเป็นผู้ช่วยที่สุภาพและเป็นกันเอง ใช้ข้อมูลจากเอกสารในการตอบคำถามให้สั้นกระชับและเข้าใจง่าย คุณสามารถจำบทสนทนาก่อนหน้าได้และสามารถอ้างอิงข้อมูลจากบทสนทนาก่อนหน้า"),
        ("system", "ประวัติการสนทนา:\n{chat_history}"),
        ("user", "คำถาม:{question}\nข้อมูลจากเอกสาร:{context}"),
    ])
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_chat_history(inputs):
        return memory.load_memory_variables({})["chat_history"]

    # Create the chain
    chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough(),
            "chat_history": get_chat_history
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain, memory

def main():
    print("กำลังเริ่มต้นระบบแชทบอท...")
    chain, memory = setup_rag_chain()
    print("\nยินดีต้อนรับสู่แชทบอท RAG ที่มีความสามารถในการจดจำบทสนทนา!")
    print("พิมพ์คำถามของคุณ หรือพิมพ์ 'exit' เพื่อออกจากโปรแกรม")
    
    while True:
        user_input = input("\nคุณ: ")
        
        if user_input.lower() in ["exit", "quit", "ออก", "จบ"]:
            print("\nแชทบอท: ขอบคุณที่ใช้บริการ ลาก่อน!")
            break
            
        if not user_input.strip():
            continue
            
        print("\nแชทบอท: กำลังค้นหาคำตอบ...")
        
        try:
            start_time = time.time()
            response = chain.invoke(user_input)
            end_time = time.time()
            
            # Save the conversation to memory
            memory.save_context({"question": user_input}, {"output": response})
            
            print(f"\nแชทบอท: {response}")
            print(f"\nใช้เวลา: {end_time - start_time:.2f} วินาที")
            
        except Exception as e:
            print(f"\nเกิดข้อผิดพลาด: {str(e)}")
            
if __name__ == "__main__":
    main() 