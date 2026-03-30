"""模块6：LLM问答生成器"""
import os
#os.environ["OPENAI_API_KEY"] = "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"
from typing import List, Dict, Any


class QAGenerator:
    def __init__(self, vector_store, model_type="openai", model_name=None):
        self.vector_store = vector_store
        self.model_type = model_type
        if model_name is None:
            if model_type == "openai":
                model_name = "gpt-3.5-turbo"
            elif model_type == "ollama":
                model_name = "llama3.2"
        self.model_name = model_name
        self._init_llm_client()
    def _init_llm_client(self):
        if self.model_type == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print(" 警告: 未设置 OPENAI_API_KEY 环境变量")
                    print("请设置: export OPENAI_API_KEY='your-key'")
                self.client = OpenAI(api_key=api_key)
                print(f"✓ OpenAI客户端已初始化，模型: {self.model_name}")
            except ImportError:
                raise ImportError("请先安装 openai 库: pip install openai")
            except Exception as e:
                print(f" OpenAI初始化失败: {e}")
                self.client = None

        elif self.model_type == "ollama":
            try:
                import requests
                self.requests = requests

                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    print(f"✓ Ollama已连接，模型: {self.model_name}")
                else:
                    print(" 无法连接到Ollama，请确保Ollama正在运行")
                self.client = True
            except ImportError:
                raise ImportError("请先安装 requests 库: pip install requests")
            except Exception as e:
                print(f"Ollama连接失败: {e}")
                print("请确保Ollama已安装并运行: https://ollama.ai/")
                self.client = None

        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def _build_prompt(self, query: str, contexts: List[Dict]) -> str:

        # 提取文本内容
        context_texts = []
        for i, ctx in enumerate(contexts):
            context_texts.append(f"[片段 {i + 1}] {ctx['content']}")

        context_str = "\n\n".join(context_texts)

        # 构建提示词
        prompt = f"""你是一个专业的学术论文助手。请基于以下论文内容回答用户的问题。

重要规则：
1. 只基于提供的论文内容回答，不要使用外部知识
2. 如果内容中没有相关信息，请诚实地说"未在论文中找到相关信息"
3. 回答要简洁、准确、有条理
4. 如果可能，引用具体的片段来支持你的回答

=== 论文内容 ===
{context_str}

=== 用户问题 ===
{query}

=== 回答 ===
"""

        return prompt

    def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的学术论文助手，基于提供的论文内容回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 降低随机性，提高准确性
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f" OpenAI API调用失败: {e}"

    def _call_ollama(self, prompt: str) -> str:
        try:
            response = self.requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                }
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f" Ollama调用失败: {response.status_code}"
        except Exception as e:
            return f" Ollama调用失败: {e}"

    def generate_answer(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        print(f"\n 正在检索与问题相关的内容...")
        print(f"问题: {query}")

        # 步骤1: 检索相关片段
        contexts = self.vector_store.search(query, top_k=top_k)

        if not contexts:
            return {
                "answer": "未找到相关论文内容，无法回答问题。",
                "contexts": [],
                "query": query,
                "model": self.model_name
            }

        print(f"✓ 检索到 {len(contexts)} 个相关片段")
        for i, ctx in enumerate(contexts):
            print(f"  - 片段 {i + 1}: 相似度 {ctx['score']:.4f}")

        # 步骤2: 构建提示词
        prompt = self._build_prompt(query, contexts)

        # 步骤3: 调用LLM生成答案
        print(f" 正在调用 {self.model_type} 模型生成答案...")

        if self.model_type == "openai":
            answer = self._call_openai(prompt)
        elif self.model_type == "ollama":
            answer = self._call_ollama(prompt)
        else:
            answer = f"不支持的模型类型: {self.model_type}"

        print(f"✓ 答案生成完成\n")

        return {
            "answer": answer,
            "contexts": contexts,
            "query": query,
            "model": f"{self.model_type}/{self.model_name}"
        }

    def generate_with_details(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        生成答案并返回详细信息（用于调试）

        Returns:
            包含更多调试信息的字典
        """
        result = self.generate_answer(query, top_k)

        # 添加提示词信息（用于调试）
        result["prompt"] = self._build_prompt(query, result["contexts"])

        return result


# 测试代码
if __name__ == "__main__":
    from vector_store import VectorStore

    # 连接已有的向量数据库
    store = VectorStore(collection_name="test_paper", persist_dir="./chroma_db")
    print(f"数据库统计: {store.get_stats()}")

    # 创建问答生成器
    print("\n" + "=" * 50)
    print("初始化问答生成器...")
    print("=" * 50)

    # 方案1: 使用OpenAI（推荐）
    # 需要设置环境变量 OPENAI_API_KEY
    qa = QAGenerator(store, model_type="ollama", model_name="llama3.2")

    # 方案2: 使用本地Ollama（免费）
    # qa = QAGenerator(store, model_type="ollama", model_name="llama3.2")

    # 测试问题
    test_queries = [
        "What is the main contribution of this paper?",
        "What methods were used in this research?",
        "What are the key findings or results?"
    ]

    for query in test_queries:
        print("\n" + "=" * 50)
        result = qa.generate_answer(query, top_k=3)

        print(f" 问题: {result['query']}")
        print(f" 模型: {result['model']}")
        print(f"\n 答案:\n{result['answer']}")
        print("\n" + "-" * 50)
        print(f" 使用的上下文片段数: {len(result['contexts'])}")

        # 可选：打印使用的片段
        # for i, ctx in enumerate(result['contexts']):
        #     print(f"\n片段 {i+1} (分数: {ctx['score']:.4f}):")
        #     print(f"{ctx['content'][:150]}...")

        input("\n按回车继续下一个问题...")