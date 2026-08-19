# 向量数据库

Qdrant 是面向向量相似度搜索的数据库，支持 collection、payload、metadata filter 和持久化。插入向量时同时保存 document_id、chunk_id、文件名、页码和原文片段，便于引用。

混合检索将向量相似度与关键词匹配融合，适合同时处理语义问题和精确技术名词。重排模型可以对候选片段进行更精细的相关性排序。
