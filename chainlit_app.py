import chainlit as cl
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Optional
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient

load_dotenv()

@cl.on_chat_start
def main():
    current_user = __current_user()
    
    # Initialize OpenAI embeddings
    os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        base_url=os.getenv("DEEPSEEK_API_BASE")
    )
    
    # Initialize Qdrant client
    client = QdrantClient(url=os.getenv("QDRANT_URL"))
    qdrant = Qdrant(
        client=client,
        collection_name="my_qdrant_test",
        embeddings=embeddings
    )
    
    # Initialize LLM
    model_name = "google/gemini-2.0-flash-001"
    llm = ChatOpenAI(model=model_name, temperature=0.7,
                     openai_api_base="https://openrouter.ai/api/v1",
                     openai_api_key=os.environ["OPEN_ROUTE_KEY"])
    
    # Create prompt templates for with and without context
    context_prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant. Use the following context to answer the user's question.
        
        Context: {context}
        
        Question: {question}
        
        Answer the question based on the context provided."""
    )
    
    no_context_prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant. Answer the user's question.
        
        Question: {question}"""
    )
    
    # Create two chains
    context_chain = LLMChain(llm=llm, prompt=context_prompt)
    no_context_chain = LLMChain(llm=llm, prompt=no_context_prompt)
    
    # Store chains and vector store in session
    cl.user_session.set("context_chain", context_chain)
    cl.user_session.set("no_context_chain", no_context_chain)
    cl.user_session.set("vectorstore", qdrant)

@cl.on_message
async def on_message(message: cl.Message):
    context_chain = cl.user_session.get("context_chain")
    no_context_chain = cl.user_session.get("no_context_chain")
    vectorstore = cl.user_session.get("vectorstore")

    try:
        # Perform similarity search
        search_results = vectorstore.similarity_search(message.content, k=2)
        
        if search_results:
            # If we found relevant context, use it
            context = "\n".join([doc.page_content for doc in search_results])
            response = context_chain.invoke({
                "context": context,
                "question": message.content
            })
        else:
            # If no relevant context found, use the no-context chain
            response = no_context_chain.invoke({
                "question": message.content
            })
        
        await cl.Message(content=response["text"]).send()
    except Exception as e:
        await cl.Message(content=f"An error occurred: {e}").send()

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user


def __current_user() -> Optional[cl.PersistedUser]:
    return cl.user_session.get("user")
