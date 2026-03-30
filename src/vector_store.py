from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
import os
class VectorStore:
    def __init__(self ,collection_name="arxiv_papers", persist_dir="./chroma_db"):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.client =chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description":"ArXiv embeddings"}
        )

    def add_documents(self, chunks, metadatas=None, ids=None):
        if ids is None:
            ids=[f"chunk_{i}"for i in range(len(chunks))]
        if metadatas is None:
            metadatas=[{"source":"unknown"}]*len(chunks)
        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

    def search(self, query, top_k=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "score": results['distances'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return formatted_results
    def search_with_score(self, query, top_k=3):
        return self.search(query, top_k)
    def get_stats(self):
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),  # 当前文档数
            "persist_dir": self.persist_dir
        }


if __name__ == "__main__":
    from pdf_parser import PDFParser
    from text_splitter import TextSplitter

    # 1. 解析PDF
    parser = PDFParser()
    text_data = parser.extract_text("./papers/2401.00001.pdf")

    # 2. 切分文本
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text_data["full_text"])

    # 3. 存入向量库
    store = VectorStore(collection_name="test_paper")
    store.add_documents(chunks)

    # 打印统计信息
    stats = store.get_stats()
    print(f"\n📊 数据库统计: {stats}")

    # 4. 测试检索
    query = "What is the main contribution of this paper?"
    results = store.search(query, top_k=2)

    # 打印检索结果
    print(f"\n🔍 检索结果 (查询: '{query}'):")
    print(f"找到 {len(results)} 个相关文档块\n")

    for i, result in enumerate(results):
        print(f"结果 {i + 1}:")
        print(f"  相似度分数: {result['score']:.4f}")  # 距离越小越相似
        print(f"  内容预览: {result['content'][:200]}...")
        print(f"  元数据: {result['metadata']}")
        print()