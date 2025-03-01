import chainlit as cl
import os
import pdb
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Dict, Optional
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable.config import RunnableConfig
from agents.react_agent import ReactAgent

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
    
    # 创建 React Agent
    react_agent = ReactAgent(
        model_name="google/gemini-2.0-flash-001",
        api_base="https://openrouter.ai/api/v1",
        api_key=os.environ["OPEN_ROUTE_KEY"]
    )
    
    # 获取 agent 和 base_prompt
    agent = react_agent.get_agent()
    base_prompt = react_agent.get_base_prompt()
    
    # 创建 qdrant prompt
    qdrant_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个有帮助的AI助手。请遵循以下原则：
        1. 始终用中文回答问题
        2. 回答要准确、清晰、简洁但信息丰富
        3. 保持专业友好的语气
        
        请使用提供的上下文来帮助回答问题。"""),
        ("system", "这是相关的上下文信息：\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    # Store components in session
    cl.user_session.set("llm", react_agent.get_llm())
    cl.user_session.set("agent", agent)
    cl.user_session.set("vectorstore", qdrant)
    cl.user_session.set("base_prompt", base_prompt)
    cl.user_session.set("qdrant_prompt", qdrant_prompt)
    cl.user_session.set("chat_history", [])

@cl.on_message
async def on_message(message: cl.Message):
    llm = cl.user_session.get("llm")
    agent = cl.user_session.get("agent")
    vectorstore = cl.user_session.get("vectorstore")
    base_prompt = cl.user_session.get("base_prompt")
    qdrant_prompt = cl.user_session.get("qdrant_prompt")
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
                prompt = qdrant_prompt
                response = llm.invoke(prompt.format_messages(
                    context=context,
                    chat_history=chat_history,
                    input=message.content
                ))
            else:
                config=RunnableConfig(
                    callbacks=[cl.LangchainCallbackHandler()],
                    configurable={"thread_id": cl.context.session.id}
                )
                final_state = agent.invoke(
                    {"messages": [HumanMessage(content=message.content)]},
                    config=config
                )
                response = final_state["messages"][-1]
            
            if not response or not response.content:
                raise ValueError("收到空的回应")

            # pdb.set_trace() 
            # Update chat history
            chat_history.extend([
                HumanMessage(content=message.content),
                response
            ])
            cl.user_session.set("chat_history", chat_history)
            
            await cl.Message(content=response.content).send()
            
        except Exception as llm_error:
            error_msg = f"处理响应时出错：{str(llm_error)}"
            await cl.Message(content=error_msg).send()
            
    except Exception as e:
        error_msg = f"处理过程中出现错误：{str(e)}"
        await cl.Message(content=error_msg).send()

# google 授权登陆
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
