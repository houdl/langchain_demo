from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

class MathClient:
    def __init__(self):
        """初始化 Math Client"""
        self.server_params = StdioServerParameters(
            command="python",
            args=["mcp_servers/math_server.py"],
        )
        self.tools = None
        self.client = None
        self.session = None
        self.read = None
        self.write = None
    
    async def initialize(self):
        """初始化连接并加载数学工具"""
        # 创建并保持连接
        self.client = stdio_client(self.server_params)
        self.read, self.write = await self.client.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        
        # 初始化连接
        await self.session.initialize()
        # 获取数学工具
        self.tools = await load_mcp_tools(self.session)
        return self.tools
    
    def get_tools(self):
        """获取已加载的数学工具"""
        return self.tools
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.client:
            await self.client.__aexit__(None, None, None)
        self.session = None
        self.client = None
        self.read = None
        self.write = None

# 示例用法
async def main():
    math_client = MathClient()
    tools = await math_client.initialize()
    print("Math tools loaded:", tools)
    await math_client.cleanup()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
