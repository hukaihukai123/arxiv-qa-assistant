from langchain_text_splitters import RecursiveCharacterTextSplitter
class TextSplitter:
    def __init__(self,chunk_size=500,chunk_overlap=50):
        self.splitter =RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
    def split_text(self,text):
        chunks=self.splitter.split_text(text)
        print(f" 已将文本切分为 {len(chunks)} 个块")
        return chunks

    def split_documents(self, documents):
        chunks = self.splitter.split_documents(documents)
        print(f" 已将 {len(documents)} 个文档切分为 {len(chunks)} 个块")
        return chunks

    def print_chunk_info(self, chunks):
        for i, chunk in enumerate(chunks[:5]):  # 只打印前5个
            print(f"\n--- 块 {i + 1} ---")
            print(f"长度: {len(chunk)} 字符")
            print(f"内容预览: {chunk[:100]}...")
if __name__ == "__main__":
    from pdf_parser import PDFParser

    # 步骤1：先用模块3解析PDF
    parser = PDFParser()
    text_data = parser.extract_text("./papers/2401.00001.pdf")

    # 步骤2：创建切分器
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

    # 步骤3：切分文本
    chunks = splitter.split_text(text_data["full_text"])

    # 步骤4：查看结果
    print(f"\n共生成 {len(chunks)} 个文本块")
    splitter.print_chunk_info(chunks)