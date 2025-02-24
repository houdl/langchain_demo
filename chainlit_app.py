import chainlit as cl
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Dict, Optional
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

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
    
    # Create chat prompt templates
    base_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant. Your responses should be:
        1. Accurate and based on the provided context when available
        2. Clear and well-structured
        3. Concise yet informative
        Please maintain a professional and friendly tone."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    context_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant. Your responses should be:
        1. Accurate and based on the provided context when available
        2. Clear and well-structured
        3. Concise yet informative
        Please maintain a professional and friendly tone."""),
        ("system", "Use this context to inform your response:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    # Store components in session
    cl.user_session.set("llm", llm)
    cl.user_session.set("vectorstore", qdrant)
    cl.user_session.set("base_prompt", base_prompt)
    cl.user_session.set("context_prompt", context_prompt)
    cl.user_session.set("chat_history", [])

@cl.on_message
async def on_message(message: cl.Message):
    llm = cl.user_session.get("llm")
    vectorstore = cl.user_session.get("vectorstore")
    base_prompt = cl.user_session.get("base_prompt")
    context_prompt = cl.user_session.get("context_prompt")
    chat_history = cl.user_session.get("chat_history")

    try:
        # Perform similarity search with scores
        search_results = vectorstore.similarity_search_with_score(message.content, k=2)
        
        try:
            # Process and filter results
            threshold = 0.6  # 相似度阈值
            relevant_docs_with_scores = [
                (doc, score) for doc, score in search_results 
                if score >= threshold
            ]
            
            if relevant_docs_with_scores:
                # Create context from relevant documents
                context = "\n\n".join([doc.page_content for doc, _ in relevant_docs_with_scores])
                prompt = context_prompt
                response = llm.invoke(prompt.format_messages(
                    context=context,
                    chat_history=chat_history,
                    input=message.content
                ))
            else:
                # Use base prompt if no context available
                prompt = base_prompt
                response = llm.invoke(prompt.format_messages(
                    chat_history=chat_history,
                    input=message.content
                ))
            
            if not response or not response.content:
                raise ValueError("Empty response received from LLM")
                
            # Update chat history
            chat_history.extend([
                HumanMessage(content=message.content),
                response
            ])
            cl.user_session.set("chat_history", chat_history)
            
            await cl.Message(content=response.content).send()
            
        except Exception as llm_error:
            error_msg = f"Error processing response: {str(llm_error)}"
            await cl.Message(content=error_msg).send()
            
    except Exception as e:
        error_msg = f"An error occurred during processing: {str(e)}"
        await cl.Message(content=error_msg).send()

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
