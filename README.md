# 📚 ArXiv 论文智能问答助手

一个基于 RAG（检索增强生成）技术的学术论文问答系统。输入 ArXiv 论文 ID，即可对论文内容进行智能问答。

## ✨ 功能特点

- 🔍 **语义检索**：基于向量相似度检索论文相关内容
- 🤖 **智能问答**：使用大语言模型生成准确答案
- 📄 **自动下载**：输入论文 ID 自动从 ArXiv 下载 PDF
- 🎨 **Web 界面**：基于 Streamlit 的友好交互界面
- 🆓 **免费可用**：支持 Ollama 本地模型，无需 API 费用

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| PDF 解析 | PyMuPDF (fitz) |
| 文本切分 | LangChain |
| 向量化模型 | sentence-transformers (all-MiniLM-L6-v2) |
| 向量数据库 | ChromaDB |
| 大语言模型 | Ollama (本地) / OpenAI API |
| Web 框架 | Streamlit |
| 编程语言 | Python 3.10+ |

## 📁 项目结构
arxiv-qa-assistant/
├── src/
│ ├── app.py # Streamlit Web 界面
│ ├── arxiv_downloader.py # ArXiv 论文下载器
│ ├── pdf_parser.py # PDF 文本解析器
│ ├── text_splitter.py # 文本切分器
│ ├── vector_store.py # 向量数据库
│ └── qa_generator.py # RAG 问答生成器
├── papers/ # 下载的 PDF 文件存放目录
├── chroma_db/ # 向量数据库持久化目录
├── requirements.txt # Python 依赖
└── README.md # 项目说明

text

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- 可选：Ollama（用于本地模型）

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/arxiv-qa-assistant.git
cd arxiv-qa-assistant
2. 创建虚拟环境
bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
3. 安装依赖
bash
pip install -r requirements.txt
4. 安装 Ollama（可选，用于本地模型）
访问 Ollama官网 下载安装，然后下载模型：

bash
ollama pull llama3.2
5. 运行应用
bash
streamlit run src/app.py
浏览器会自动打开 http://localhost:8501

📖 使用指南
基本流程
输入论文 ID：在左侧输入 ArXiv 论文 ID（如 1706.03762）

加载论文：点击「下载并加载论文」，系统自动下载 PDF 并建立向量索引

提问：在右侧输入问题，点击「提问」

查看答案：系统返回基于论文内容的答案，并显示检索到的相关片段

示例论文 ID
论文 ID	标题
1706.03762	Attention Is All You Need (Transformer)
2303.08774	GPT-4 Technical Report
2401.00001	示例论文
2106.09685	LoRA: Low-Rank Adaptation
示例问题
What is the main contribution of this paper?

What methods were used in the experiments?

What datasets were used?

What are the limitations mentioned?

⚙️ 配置说明
模型选择
模型类型	说明	费用
Ollama (本地)	需要安装 Ollama，完全免费	免费
OpenAI API	需要 API Key，效果更好	按量付费
检索参数
文本块大小：每个文本块的最大字符数（默认 500）

块重叠：相邻块之间的重叠字符数（默认 50）

检索片段数：每次检索返回的相关片段数量（默认 3）

📊 工作流程
text
用户输入论文 ID
       ↓
下载 PDF 文件
       ↓
提取文本内容
       ↓
切分为文本块 (chunks)
       ↓
生成向量并存入 ChromaDB
       ↓
用户输入问题
       ↓
语义检索相关文本块
       ↓
构建提示词 (Prompt)
       ↓
调用 LLM 生成答案
       ↓
返回答案并显示检索片段
🔧 依赖说明
requirements.txt
txt
streamlit>=1.35.0
arxiv>=2.0.0
pymupdf>=1.23.0
langchain>=0.3.0
langchain-community>=0.3.0
langchain-chroma>=0.1.0
chromadb>=0.5.0
sentence-transformers>=3.0.0
openai>=1.0.0
📝 开发说明
模块功能
模块	功能
arxiv_downloader.py	从 ArXiv 下载论文 PDF 和元数据
pdf_parser.py	解析 PDF 提取纯文本
text_splitter.py	将长文本切分为语义完整的块
vector_store.py	向量化存储和语义检索
qa_generator.py	RAG 问答生成
app.py	Streamlit Web 界面
运行测试
bash
# 测试下载器
python src/arxiv_downloader.py

# 测试 PDF 解析
python src/pdf_parser.py

# 测试向量存储
python src/vector_store.py

# 测试问答生成
python src/qa_generator.py

# 启动 Web 应用
streamlit run src/app.py
🎯 项目亮点
完整的 RAG 实现：从 PDF 解析到向量检索到 LLM 生成

模块化设计：各模块独立，便于扩展和维护

本地部署友好：支持 Ollama，无需 GPU 和 API 费用

交互式界面：Streamlit 提供直观的 Web 操作界面

📄 License
MIT License

👨‍💻 作者
胡凯 - 上海交通大学钱学森班

🙏 致谢
ArXiv 提供的论文数据

LangChain RAG 框架

Streamlit Web 框架

Ollama 本地 LLM 支持