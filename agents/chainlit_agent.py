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

        3. 使用 PostgreSQL 工具的情况：
           - execute_query: 执行只读SQL查询
             * 输入参数：sql (string类型)
             * 在READ ONLY事务中执行
             * 用于查询数据库中的数据
           - get_table_schema: 获取数据库表结构信息
             * 返回表的JSON schema信息
             * 包含列名和数据类型
             * 用于了解数据库结构
           - 表主要是feedmob 系统的业务功能，下面是如何获取一个 client 的net_spend 的过程，表的关联关系如下举例：
             * clients 表获取 Uber Technologies 的 client id, 如果提到 uber 相关的 client 都是指的 client name = Uber Technologies
             * 根据client_id 从 campaigns表 获取对应 client 的 campaigns
             * vendors 表获取 jampp 的 vendor_id
             * 根据获取的 campaign_id 以及 vendor_id 获取 net_spends 表的 spend 数据, 其中 net_spends 表中  net_spend_cents/100.0 就是 uber 的 net spend ，net_spends 表中的 spend_date 时需要查询的日期

        4. 使用 Jampp 工具的情况：
           - get_jampp_all_supported_clients: 获取所有支持的广告客户端列表
             * 用于查看可用的客户端
             * 用于确认客户端名称是否有效
           - get_jampp_reports: 获取广告报告数据
             * 需要提供：客户端名称、开始日期、结束日期
             * 返回广告活动的详细数据（展示、点击、转化、支出等）
             * 用于分析广告效果和投资回报
           - 可以使用 PostgreSQL中的 jampp_campaign_mappings表 来进行关联 PostgreSQL 中的数据
             * jampp_campaign_mappings 是用来获取 jampp api 的数据 如何 进行 mapping 到 net_spends 表中的数据的
             * jampp_campaign_mappings 中的 jampp_campaign_id 是 jampp api 数据中的 中的 campaign id
             * jampp_campaign_mappings 中的 vendor_id 以及 campaign_id 就是对应 net_spends 中的 vendor_id 以及 campaign_id
             * jampp_campaign_mappings 表中 一个 campaign_id 可能有多个 jampp campaign id，这个方便进行聚合对比数据

        5. 使用 TestTool 工具的情况：
           - 当询问test tool的时候时候

        6. 使用 Iron Source 工具的情况：
           - fetch_reports: 获取特定广告活动的报告数据
             * 需要提供：开始日期、结束日期、campaign IDs列表
             * 返回广告活动的详细数据（展示、点击、完成、安装、支出等）
             * 用于分析特定广告活动的效果
           - fetch_reports_by_bundleids: 获取特定应用包ID的报告数据
             * 需要提供：开始日期、结束日期、bundle IDs列表
             * 返回应用包相关的广告数据
             * 用于分析特定应用的广告效果
           - fetch_all_reports: 获取所有报告数据
             * 需要提供：开始日期、结束日期
             * 返回所有广告活动的数据
             * 用于全面分析广告效果

        7. 直接回答（不使用工具）的情况：
           - 基础知识问题
           - 可以基于已有知识可靠回答的问题

        在使用搜索工具前，请先判断是否真的需要外部信息。
        所有回答必须用中文，即使搜索结果是英文也要翻译成中文。"""),
        ("placeholder", "{messages}")
    ])

    return prompt
