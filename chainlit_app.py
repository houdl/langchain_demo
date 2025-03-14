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
    model_name = "deepseek-ai/DeepSeek-V2.5"
    react_agent = ReactAgent(
        model_name=model_name,
        api_base=os.getenv("DEEPSEEK_API_BASE"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        checkpointer=checkpointer
    )
    await react_agent.initialize()

    # Store components in session
    cl.user_session.set("react_agent", react_agent)

@cl.on_message
async def on_message(message: cl.Message):
    react_agent = cl.user_session.get("react_agent")

    try:
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler()],
            configurable={"thread_id": cl.context.session.id}
        )
        final_state = await react_agent.get_agent().ainvoke(
            {"messages": [HumanMessage(content=message.content)]},
            config=config
        )
        response = final_state["messages"][-1]

        await cl.Message(content=response.content).send()

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
