import logging
import pdb
import chainlit as cl
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from agents.chainlit_agent import create_chainlit_agent
from agents.qdrant_agent import QdrantAgent

load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    current_user = __current_user()

    # 创建共享的 checkpointer
    checkpointer = MemorySaver()
    # Store components in session
    cl.user_session.set("checkpointer", checkpointer)

@cl.on_message
async def on_message(message: cl.Message):
    checkpointer = cl.user_session.get("checkpointer")
    chainlit_agent = create_chainlit_agent(checkpointer=checkpointer)

    try:
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler()],
            configurable={"thread_id": '12122'}
        )
        final_state = await chainlit_agent.ainvoke(
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
