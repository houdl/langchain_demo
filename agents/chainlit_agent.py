from typing import Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from agents.tools.test import TestTool
from bedrock_service import BedrockAIService, BedrockModel
from mcp_client import get_mcp_tools

def create_chainlit_agent(checkpointer: Optional[MemorySaver] = None):
    llm = BedrockAIService().llm_converse(model=BedrockModel.PRO_MODEL_ID.value)

    tools = get_mcp_tools()
    tools.extend(
        [
            TestTool(),
            DuckDuckGoSearchRun()
        ]
    )

    agent = create_react_agent(
        llm,
        tools=tools,
        prompt=__system_prompt(),
        checkpointer=checkpointer
    )
    return agent


def __system_prompt() -> Any:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个有帮助的AI助手。请遵循以下原则：
        1. 回答要准确、清晰、简洁但信息丰富
        2. 保持专业友好的语气

        工具使用指南：
        1. 使用 DuckDuckGoSearchRun 工具的情况：
           - 需要最新新闻或当前事件信息
           - 需要实时数据或统计，例如股票，天气等
           - 需要验证具体事实
           - 需要最新或特定信息时

        2. 使用数学工具的情况：
           - 需要进行精确的数学计算
           - add: 用于加法运算
           - multiply: 用于乘法运算
           - 当需要确保计算准确性时

        3. 使用 Jampp 工具的情况：
           - get_jampp_all_supported_clients: 获取所有支持的广告客户端列表
             * 用于查看可用的客户端
             * 用于确认客户端名称是否有效
           - get_jampp_reports: 获取广告报告数据
             * 需要提供：客户端名称、开始日期、结束日期
             * 返回广告活动的详细数据（展示、点击、转化、支出等）
             * 用于分析广告效果和投资回报

        4. 使用 TestTool 工具的情况：
           - 当询问test tool的时候时候

        5. 直接回答（不使用工具）的情况：
           - 基础知识问题
           - 可以基于已有知识可靠回答的问题

        在使用搜索工具前，请先判断是否真的需要外部信息。
        所有回答必须用中文，即使搜索结果是英文也要翻译成中文。"""),
        ("placeholder", "{messages}")
    ])

    return prompt
