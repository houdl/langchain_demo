import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
import pdb
import requests

load_dotenv()


# 1. 准备数据
loader = TextLoader("docs/all-ping.md")  # 替换为你的数据文件
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# 2. 创建 Qdrant 客户端
QDRANT_URL = os.getenv("QDRANT_URL")
client = QdrantClient(url=QDRANT_URL)

# 3. 选择 Embedding 模型
os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")
# pdb.set_trace()  # 设置断点
embeddings = OpenAIEmbeddings(model="BAAI/bge-m3",base_url=os.getenv("DEEPSEEK_API_BASE"))

# 4. 创建向量数据库
collection_name = "my_qdrant_test"  # 替换为你的集合名称
qdrant = Qdrant.from_documents(docs, embeddings, url=QDRANT_URL, collection_name=collection_name,force_recreate=True)  # 如果集合已存在，则强制重新创建

print(f"向量数据库已成功创建并保存到 Qdrant 集合: {collection_name}")
