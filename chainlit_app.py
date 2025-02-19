import chainlit as cl
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Optional

load_dotenv()

@cl.on_chat_start
def main():
    current_user = __current_user()
    model_name = "google/gemini-2.0-flash-001"
    llm = ChatOpenAI(model=model_name, temperature=0.7,
                     openai_api_base="https://openrouter.ai/api/v1",
                     openai_api_key=os.environ["OPEN_ROUTE_KEY"])
    prompt_template = ChatPromptTemplate.from_template("You are a helpful assistant. Answer the user's question.\n\nQuestion: {question}")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    cl.user_session.set("chain", chain)

@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("chain")

    try:
        response = chain.invoke({"question": message.content})
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
