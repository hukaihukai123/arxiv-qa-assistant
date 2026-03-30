import arxiv
import os
import requests
class ArxivDownloader:
    def __init__(self,download_dir="./papers"):
        self.download_dir = download_dir
        self.client =arxiv.Client()
        os.makedirs(download_dir,exist_ok=True)
    def download_papers(self,paper_id):
        search=arxiv.Search(id_list=[paper_id])
        try:
            paper=next(self.client.results(search))
        except StopIteration:
            print("No results for paper_id")
            return None
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        pdf_path=os.path.join(self.download_dir,f"{paper_id}.pdf")
        # 使用 requests 下载 PDF，绕过 SSL 验证（如果需要）
        try:
            response = requests.get(pdf_url, verify=True)  # verify=True 验证证书
            response.raise_for_status()

            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ 已下载: {paper.title}")
        except requests.exceptions.SSLError:
            # 如果 SSL 验证失败，尝试不验证（仅用于开发环境）
            print("SSL 验证失败，尝试绕过验证...")
            response = requests.get(pdf_url, verify=False)
            response.raise_for_status()
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ 已下载: {paper.title}")
        return {
            "id":paper_id,
            "title":paper.title,
            "authors":[author.name for author in paper.authors],
            "summary":paper.summary,
            "published":paper.published,
            "pdf_path":pdf_path
        }
    def search_and_download(self,query,max_results=1):
        search=arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        papers=[]
        for paper in self.client.results(search):
            paper_id=paper.get_short_id()
            info=self.download_papers(paper_id)
            if info:
                papers.append(info)
        return papers
if __name__ == "__main__":
    downloader = ArxivDownloader()           # 创建下载器实例
    info = downloader.download_papers("2401.00001")  # 下载示例论文