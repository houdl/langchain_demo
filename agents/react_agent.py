from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from bedrock_service import BedrockAIService, BedrockModel
from mcp_client import get_mcp_tools

class ReactAgent:
    def __init__(self, checkpointer: MemorySaver = None):
        """初始化 React Agent

        Args:
            checkpointer: 用于保存对话历史的 MemorySaver 实例
        """
        self.llm = None
        self.agent = None
        self.base_prompt = None
        self.checkpointer = checkpointer

    @staticmethod
    @tool
    def web_search(query: str):
        """用于搜索需要实时信息或验证的内容。
        适用场景：
        - 需要最新新闻或当前事件信息
        - 需要实时数据或统计信息
        - 需要特定的事实验证
        不要用于：
        - 基础知识问题
        - 简单的逻辑运算
        - 可以直接回答的问题"""
        search = DuckDuckGoSearchRun()
        return search.run(query)

    def _create_base_prompt(self):
        """创建基础提示模板"""
        return ChatPromptTemplate.from_messages([
            ("system", """你是一个有帮助的AI助手。请遵循以下原则：
            1. 始终用中文回答问题
            2. 回答要准确、清晰、简洁但信息丰富
            3. 保持专业友好的语气

            工具使用指南：
            1. 使用 'web_search' 工具的情况：
               - 需要最新新闻或当前事件信息
               - 需要实时数据或统计，例如股票，天气等
               - 需要验证具体事实
               - 需要最新或特定信息时

            2. 使用数学工具的情况：
               - 需要进行精确的数学计算
               - add: 用于加法运算
               - multiply: 用于乘法运算
               - 当需要确保计算准确性时

            3. 直接回答（不使用工具）的情况：
               - 基础知识问题
               - 可以基于已有知识可靠回答的问题

            在使用搜索工具前，请先判断是否真的需要外部信息。
            所有回答必须用中文，即使搜索结果是英文也要翻译成中文。"""),
            ("placeholder", "{messages}")
        ])

    def initialize(self, checkpointer=None):
        """异步初始化 Agent 的所有组件

        Args:
            checkpointer: checkpointer 实例，用于保存对话历史
        """
        # 初始化 LLM
        self.llm = BedrockAIService().llm_converse(model=BedrockModel.PRO_MODEL_ID.value)


        # 创建基础提示模板
        self.base_prompt = self._create_base_prompt()

        # 初始化 math client
        mcp_tools = get_mcp_tools()

        # 定义工具列表
        tools = [self.web_search]
        tools.extend(mcp_tools)

        # 创建 agent
        self.agent = create_react_agent(
            self.llm,
            tools,
            checkpointer=checkpointer,
            prompt=self.base_prompt
        )

    def get_agent(self):
        """获取初始化好的 agent"""
        return self.agent

    def get_base_prompt(self):
        """获取基础提示模板"""
        return self.base_prompt

    def get_llm(self):
        """获取初始化好的 LLM"""
        return self.llm

    async def cleanup(self):
        """清理资源"""
        if hasattr(self, 'math_client') and self.math_client:
            await self.math_client.cleanup()
