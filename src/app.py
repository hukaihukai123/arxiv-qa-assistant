"""
模块7：ArXiv论文问答系统 - Web界面
"""
import streamlit as st
import os
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.append(str(Path(__file__).parent))

from arxiv_downloader import ArxivDownloader
from pdf_parser import PDFParser
from text_splitter import TextSplitter
from vector_store import VectorStore
from qa_generator import QAGenerator

# 页面配置
st.set_page_config(
    page_title="ArXiv论文问答助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS（让界面更好看）
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .paper-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'is_ready' not in st.session_state:
    st.session_state.is_ready = False
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'qa_generator' not in st.session_state:
    st.session_state.qa_generator = None
if 'paper_info' not in st.session_state:
    st.session_state.paper_info = None
if 'chunks_count' not in st.session_state:
    st.session_state.chunks_count = 0

# ==================== 侧边栏配置 ====================
with st.sidebar:
    st.image("https://arxiv.org/static/browse/0.3.4/images/arxiv-logo-web.svg", width=150)
    st.markdown("### ⚙️ 配置")

    # 模型选择
    model_option = st.radio(
        "选择LLM模型",
        ["Ollama (本地模型)", "OpenAI API"],
        help="推荐使用Ollama本地模型，完全免费"
    )

    if "OpenAI" in model_option:
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        model_type = "openai"
        model_name = "gpt-3.5-turbo"
    else:
        model_type = "ollama"
        model_name = st.selectbox(
            "选择Ollama模型",
            ["llama3.2", "qwen2.5:1.5b", "phi3:mini", "llama3.2:1b"],
            help="需要先在Ollama中下载对应模型"
        )

    st.divider()

    st.markdown("### 🔧 检索参数")
    chunk_size = st.slider("文本块大小 (字符)", 200, 800, 500,
                           help="每个文本块的最大字符数")
    chunk_overlap = st.slider("块重叠 (字符)", 0, 200, 50,
                              help="相邻块之间的重叠字符数")
    top_k = st.slider("检索片段数", 1, 10, 3,
                      help="每次检索返回的相关片段数量")

    st.divider()

    st.markdown("### 📊 状态")
    if st.session_state.is_ready:
        st.success("✅ 系统就绪")
        st.info(f"📄 论文: {st.session_state.paper_info['title'][:50]}...")
        st.info(f"🔢 文档块: {st.session_state.chunks_count}")
    else:
        st.warning("⏳ 未加载论文")

# ==================== 主界面 ====================
st.markdown('<p class="main-header">📚 ArXiv论文智能问答助手</p>', unsafe_allow_html=True)
st.markdown("输入ArXiv论文ID，下载论文后可以提问任何关于论文的问题")

# 创建两列布局
col1, col2 = st.columns([1, 1])

# ==================== 左侧：加载论文 ====================
with col1:
    st.subheader("📥 1. 加载论文")

    # 论文ID输入
    paper_id = st.text_input(
        "ArXiv论文ID",
        placeholder="例如: 1706.03762 (Attention is All You Need)",
        help="可以从 arxiv.org 找到论文ID"
    )

    # 加载按钮
    if st.button("📥 下载并加载论文", type="primary", use_container_width=True):
        if not paper_id:
            st.error("请输入论文ID")
        else:
            with st.spinner(f"正在下载论文 {paper_id}..."):
                try:
                    # 1. 下载论文
                    downloader = ArxivDownloader(download_dir="./papers")
                    paper_info = downloader.download_papers(paper_id)

                    if paper_info:
                        st.session_state.paper_info = paper_info

                        # 2. 解析PDF
                        parser = PDFParser()
                        text_data = parser.extract_text(paper_info["pdf_path"])

                        # 3. 切分文本
                        splitter = TextSplitter(chunk_size=chunk_size,
                                                chunk_overlap=chunk_overlap)
                        chunks = splitter.split_text(text_data["full_text"])
                        st.session_state.chunks_count = len(chunks)

                        # 4. 存入向量库
                        collection_name = f"paper_{paper_id.replace('.', '_')}"
                        vector_store = VectorStore(
                            collection_name=collection_name,
                            persist_dir="./chroma_db"
                        )
                        vector_store.add_documents(chunks)
                        st.session_state.vector_store = vector_store

                        # 5. 初始化问答生成器
                        qa = QAGenerator(
                            vector_store,
                            model_type=model_type,
                            model_name=model_name
                        )
                        st.session_state.qa_generator = qa
                        st.session_state.is_ready = True

                        st.success(f"✅ 论文加载成功！")

                except Exception as e:
                    st.error(f"❌ 加载失败: {e}")
                    import traceback

                    st.code(traceback.format_exc())

    # 显示已加载论文信息
    if st.session_state.paper_info:
        info = st.session_state.paper_info
        with st.expander("📄 论文信息", expanded=True):
            st.markdown(f"**标题:** {info['title']}")
            st.markdown(f"**作者:** {', '.join(info['authors'][:3])}" +
                        ("..." if len(info['authors']) > 3 else ""))
            st.markdown(f"**发布日期:** {info['published'].strftime('%Y-%m-%d')}")
            st.markdown(f"**摘要预览:**")
            st.text(info['summary'][:300] + "...")
            st.markdown(f"**PDF路径:** `{info['pdf_path']}`")

# ==================== 右侧：问答区域 ====================
with col2:
    st.subheader("💬 2. 提问")

    # 检查系统是否就绪
    if not st.session_state.is_ready:
        st.info("👈 请先在左侧加载一篇论文")
    else:
        # 问题输入
        question = st.text_area(
            "输入你的问题",
            placeholder="例如:\n- What is the main contribution of this paper?\n- What methods were used?\n- What datasets were used in experiments?",
            height=120
        )

        # 示例问题按钮
        st.markdown("**💡 示例问题:**")
        col_q1, col_q2 = st.columns(2)

        example_questions = [
            "What is the main contribution?",
            "What methods were used?",
            "What datasets were used?",
            "What are the key findings?"
        ]

        for i, q in enumerate(example_questions):
            if i % 2 == 0:
                if col_q1.button(q, key=f"ex_{i}", use_container_width=True):
                    question = q
            else:
                if col_q2.button(q, key=f"ex_{i}", use_container_width=True):
                    question = q

        # 提问按钮
        if st.button("🔍 提问", type="primary", use_container_width=True):
            if not question:
                st.warning("请输入问题")
            else:
                with st.spinner("正在检索并生成答案..."):
                    try:
                        # 生成答案
                        result = st.session_state.qa_generator.generate_answer(
                            question,
                            top_k=top_k
                        )

                        # 显示答案
                        st.markdown("### 🤖 答案")
                        st.markdown(
                            f'<div class="answer-box">{result["answer"]}</div>',
                            unsafe_allow_html=True
                        )

                        # 显示模型信息
                        st.caption(f"模型: {result['model']} | 检索片段数: {len(result['contexts'])}")

                        # 显示检索到的相关片段（可折叠）
                        with st.expander("📚 查看检索到的相关片段"):
                            for i, ctx in enumerate(result["contexts"]):
                                st.markdown(f"**片段 {i + 1}** (相似度: {ctx['score']:.4f})")
                                st.markdown(f"```\n{ctx['content'][:500]}...\n```")
                                if i < len(result["contexts"]) - 1:
                                    st.divider()

                    except Exception as e:
                        st.error(f"❌ 生成答案失败: {e}")
                        import traceback

                        st.code(traceback.format_exc())

# ==================== 页脚 ====================
st.divider()
st.caption("💡 提示: 首次加载论文需要下载PDF并建立向量索引，请耐心等待")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 如何使用

    1. **输入论文ID**: 在左侧输入ArXiv论文ID（如 `1706.03762`）
    2. **点击加载**: 系统会自动下载PDF并建立向量索引
    3. **输入问题**: 在右侧输入关于论文的任何问题
    4. **获取答案**: 系统会检索相关内容并生成答案

    ### 支持的模型

    - **Ollama本地模型** (推荐): 免费，需要先安装Ollama并下载模型
    - **OpenAI API**: 效果更好，但需要API Key和付费

    ### 示例论文ID

    - `1706.03762` - Attention is All You Need (Transformer)
    - `2401.00001` - 示例论文
    - `2303.08774` - GPT-4技术报告

    ### 技术栈

    - PDF解析: PyMuPDF
    - 向量化: sentence-transformers (all-MiniLM-L6-v2)
    - 向量数据库: ChromaDB
    - LLM: Ollama / OpenAI
    - Web框架: Streamlit
    """)