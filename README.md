

# 使用 nv 进行环境设置


# 导入数据
python3.12 create_qdrant_db.py

# 运行 mcp server
fastmcp dev mcp_servers/math_server.py

# 如何执行
chainlit run chainlit_app.py -w