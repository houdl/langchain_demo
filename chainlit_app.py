import logging
import pdb
import chainlit as cl
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from agents.react_agent import ReactAgent
from agents.qdrant_agent import QdrantAgent

load_dotenv()

@cl.on_chat_end
async def on_chat_end():
    """聊天会话结束时的清理"""
    try:
        react_agent = cl.user_session.get("react_agent")
        if react_agent:
            await react_agent.cleanup()
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

@cl.on_stop
async def on_stop():
    """应用停止时的清理"""
    await on_chat_end()

@cl.on_chat_start
async def main():
    current_user = __current_user()
    
    # 创建共享的 checkpointer
    checkpointer = MemorySaver()
    
    # 创建并初始化 React Agent
    model_name = "google/gemini-2.0-flash-001"
    react_agent = ReactAgent(
        model_name=model_name,
        api_base="https://openrouter.ai/api/v1",
        api_key=os.environ["OPEN_ROUTE_KEY"],
        checkpointer=checkpointer
    )
    await react_agent.initialize(checkpointer)
    
    # 创建 Qdrant Agent
    qdrant_agent = QdrantAgent(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        api_base=os.getenv("DEEPSEEK_API_BASE"),
        qdrant_url=os.getenv("QDRANT_URL"),
        collection_name="my_qdrant_test"
    )
    
    # Store components in session
    cl.user_session.set("react_agent", react_agent)
    cl.user_session.set("qdrant_agent", qdrant_agent)
    cl.user_session.set("chat_history", [])

@cl.on_message
async def on_message(message: cl.Message):
    react_agent = cl.user_session.get("react_agent")
    qdrant_agent = cl.user_session.get("qdrant_agent")
    chat_history = cl.user_session.get("chat_history")
    
    try:
        # 搜索相似文档
        context = qdrant_agent.search_similar(message.content)
        
        try:
            if context:
                # 使用向量存储结果
                prompt = qdrant_agent.get_prompt()
                response = await react_agent.get_llm().ainvoke(prompt.format_messages(
                    context=context,
                    chat_history=chat_history,
                    input=message.content
                ))
            else:
                config=RunnableConfig(
                    callbacks=[cl.LangchainCallbackHandler()],
                    configurable={"thread_id": cl.context.session.id}
                )
                final_state = await react_agent.get_agent().ainvoke(
                    {"messages": [HumanMessage(content=message.content)]},
                    config=config
                )
                response = final_state["messages"][-1]
            
            if not response or not response.content:
                raise ValueError("收到空的回应")

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
