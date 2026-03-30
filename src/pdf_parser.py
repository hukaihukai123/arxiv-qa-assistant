import fitz
import os
class PDFParser:
    def __init__(self):
        pass
    def extract_text(self,pdf_path):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError("PDF file not found")
        doc = fitz.open(pdf_path)
        all_text=[]
        for page_num,page in enumerate(doc):
            text =page.get_text()
            if text.strip():
                all_text.append({"page":page_num+1,"text":text})
        doc.close()
        full_text="\n\n".join([p["text"] for p in all_text])
        print(f"✓ 已提取 {len(all_text)} 页文本，共 {len(full_text)} 字符")
        return {
                "full_text": full_text,  # 完整文本
                "pages": all_text,  # 分页文本
                "page_count": len(all_text)  # 总页数
        }
    def extract_text_simple(self,pdf_path):
        result=self.extract_text(pdf_path)
        return result["full_text"]
if __name__ == "__main__":
    parser=PDFParser()
    test_pdf = "./papers/2401.00001.pdf"
    if os.path.exists(test_pdf):
        text_data = parser.extract_text(test_pdf)  # 提取文本
        print(f"\n文本预览（前500字符）：")
        print(text_data["full_text"][:500])  # 显示前500字符
    else:
        print("请先运行模块2下载一篇论文")