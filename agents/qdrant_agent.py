from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class QdrantAgent:
    def __init__(self, api_key: str, api_base: str, qdrant_url: str, collection_name: str):
        """初始化 Qdrant Agent

        Args:
            api_key: OpenAI API密钥
            api_base: OpenAI API基础URL
            qdrant_url: Qdrant服务器URL
            collection_name: Qdrant集合名称
        """
        self.api_key = api_key
        self.api_base = api_base
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.embeddings = None
        self.vectorstore = None
        self.qdrant_prompt = None
        self._initialize()

    def _initialize(self):
        """初始化 Qdrant Agent 的所有组件"""
        # 初始化 embeddings
        self.embeddings = OpenAIEmbeddings(
            model="BAAI/bge-m3",
            base_url=self.api_base,
            openai_api_key=self.api_key
        )

        # 初始化 Qdrant client
        client = QdrantClient(url=self.qdrant_url)

        # 初始化向量存储
        self.vectorstore = Qdrant(
            client=client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )

        # 创建 qdrant prompt
        self.qdrant_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个有帮助的AI助手。请遵循以下原则：
            1. 始终用中文回答问题
            2. 回答要准确、清晰、简洁但信息丰富
            3. 保持专业友好的语气

            请使用提供的上下文来帮助回答问题。"""),
            ("system", "这是相关的上下文信息：\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

    def search_similar(self, query: str, k: int = 7, threshold: float = 0.55):
        """搜索相似文档

        Args:
            query: 搜索查询
            k: 返回的最大文档数量
            threshold: 相似度阈值

        Returns:
            list: 相关文档列表及其内容
        """
        # 执行相似度搜索
        search_results = self.vectorstore.similarity_search_with_score(query, k=k)

        # 过滤结果
        relevant_docs = [
            (doc, score) for doc, score in search_results
            if score >= threshold
        ]

        if relevant_docs:
            # 提取文档内容
            context = "\n\n".join([doc.page_content for doc, _ in relevant_docs])
            return context

        return None

    def get_vectorstore(self):
        """获取向量存储实例"""
        return self.vectorstore

    def get_prompt(self):
        """获取 Qdrant prompt 模板"""
        return self.qdrant_prompt
