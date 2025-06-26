import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def chat_with_context(user_id, course_id, query):
    namespace = f"{user_id}-{course_id}"
    history = get_session_history(namespace)

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("upskill")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)

    docs = vectorstore.similarity_search(query, k=4)
    context = "\n\n".join([d.page_content for d in docs]) if docs else "Không có tài liệu liên quan."

    template = """Bạn là trợ lý học tập. Dựa vào ngữ cảnh sau, trả lời câu hỏi:

    NGỮ CẢNH:
    {context}

    Câu hỏi mới: {question}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    chain = (
        {
            "context": lambda _: context,
            "history": lambda _: history.messages,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    conversational_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": namespace}}
    response = conversational_chain.invoke({"question": query}, config=config)
    return {"response": response}