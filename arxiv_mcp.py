from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel,Field
import arxiv
import os

mcp = FastMCP()

DOWNLOAD_PATH: str =  os.getenv("DOWNLOAD_PATH")
PAPER_CACHE: dict[str:arxiv.Result] = {}

class PaperInfo(BaseModel):
    id:str = Field(description ="\u5b8c\u6574\u8bba\u6587 ID(\u542b\u7248\u672c\u53f7)"),
    title:str = Field(description = "\u8bba\u6587\u6807\u9898"),
    abstract:str = Field(description = "\u8bba\u6587\u6458\u8981"),
    categories: list[str] = Field(description = "\u8bba\u6587\u7684arXiv\u5206\u7c7b\u5217\u8868"),
    authors: list[str] = Field(description = "\u8bba\u6587\u4f5c\u8005\u5217\u8868"),
    pdf_url: str|None = Field(description = "\u8bba\u6587PDF\u8bbf\u95ee\u94fe\u63a5"),
    publish_date: str = Field(description = "\u8bba\u6587\u9996\u6b21\u63d0\u4ea4\u65f6\u95f4(UTC\u65f6\u533a)"),
    journal_ref: str|None = Field(description ="\u671f\u520a\u5f15\u7528\u4fe1\u606f"),
    doi: str|None = Field(description = "doi\u7f16\u53f7")

class QueryErrorResult(BaseModel):
    query:str = Field(description = "\u8f93\u5165\u7684\u67e5\u8be2\u8bed\u53e5"),
    error_info:str = Field(description = "\u62a5\u9519\u4fe1\u606f")

class DownloadSuccessResult(BaseModel):
    download_result:str = Field(description = "\u4e0b\u8f7d\u7ed3\u679c"),
    message:str = Field(description = "\u4e0b\u8f7d\u6210\u529f\u7684\u8865\u5145\u4fe1\u606f")

class DownloadErrorResult(BaseModel):
    download_result:str = Field(description = "\u4e0b\u8f7d\u7ed3\u679c"),
    message:str = Field(description = "\u4e0b\u8f7d\u5931\u8d25\u7684\u8865\u5145\u4fe1\u606f"),
    undo_ids:list[str] = Field(description = "\u4e0b\u8f7d\u5931\u8d25\u7684\u8bba\u6587\u7684arxiv id\u5217\u8868 ")

@mcp.tool(
    name="query_paper",
    description="\u6839\u636e\u751f\u6210\u7684query\u8bed\u53e5\u641c\u7d22arXiv\u8bba\u6587,\u6839\u636e\u7528\u6237\u610f\u56de\u8fd9\u76f8\u5173\u8bba\u6587\u4fe1\u606f,\u5982\u67e5\u8be2\u4e2d\u51fa\u73b0\u5f02\u5e38,\u9700\u5411\u7528\u6237\u63d0\u4f9b\u67e5\u8be2\u7684return"
)
def query_paper(
    query:str|list[str] = Field(
        description = """
            \u641c\u7d22\u5173\u952e\u8bcd / \u8868\u8fbe\u5f0f\uff08\u652f\u6301 arXiv \u539f\u751f\u68c0\u7d22\u8bed\u6cd5\uff09 
            - \u5355\u5173\u952e\u8bcd\uff1a\"transformer\"
            - \u591a\u6761\u4ef6\uff1a\"title:transformer AND author:attention\"
            - \u5217\u8868\u5f62\u5f0f\uff1a[\"transformer\", \"attention\"]\uff08\u591a\u5173\u952e\u8bcd OR \u903b\u8f91\uff09
            """,
        examples = ["transformer","title:transformer AND author:attention",["transformer", "attention"]]
    ), 
    max_results:int = Field(
        description = "\u8fd4\u8bba\u6587\u7684\u6700\u5927\u6570\u91cf",
        default = 5
    ),
    sort_by:arxiv.SortCriterion = Field(
        description = 
        """
            \u5bf9\u7ed3\u679c\u6392\u5e8f\u7684\u89c4\u5219,\u53ef\u9009\u503c\uff1a
            - arxiv.SortCriterion.Relevance(\u76f8\u5173\u6027\uff0c\u9ed8\u8ba4)
            - arxiv.SortCriterion.SubmittedDate(\u63d0\u4ea4\u65f6\u95f4\uff0c\u6700\u65b0\u4f18\u5148)
            - arxiv.SortCriterion.LastUpdatedDate(\u6700\u540e\u66f4\u65b0\u65f6\u95f4)
        """,
        default = arxiv.SortCriterion.Relevance,
        json_schema_extra= {"enum":[arxiv.SortCriterion.Relevance,arxiv.SortCriterion.SubmittedDate,arxiv.SortCriterion.LastUpdatedDate]}
    ),
    sort_order:arxiv.SortOrder = Field(
        description = 
        """
            \u6392\u5e8f\u987a\u5e8f\uff0c\u53ef\u9009\u503c\uff1a
            - arxiv.SortOrder.Descending(\u964d\u5e8f)
            - arxiv.SortOrder.Ascending(\u5347\u5e8f)
        """,
        json_schema_extra={"enum":[arxiv.SortOrder.Descending,arxiv.SortOrder.Ascending]}
    )
) -> list[PaperInfo]|QueryErrorResult:
    try:
        global PAPER_CACHE
        PAPER_CACHE.clear()
        
        search = arxiv.Search(query,max_results = max_results,sort_by = sort_by,sort_order = sort_order)
        client = arxiv.Client()
        papers = []
        for paper in client.results(search):
            PAPER_CACHE[paper.get_short_id()] = paper

            papers.append(
                PaperInfo(
                    id = paper.get_short_id(),
                    title = paper.title,
                    abstract = paper.summary,
                    categories = paper.categories,
                    authors = [author.name for author in paper.authors],
                    pdf_url = paper.pdf_url,
                    publish_date = str(paper.published),  
                    journal_ref = paper.journal_ref,
                    doi = paper.doi
                )
            )
        return papers
    except Exception as e:
        return QueryErrorResult(query = query,error_info = repr(e))
    
@mcp.tool(
    name="download_paper",
    description="\u5f53\u7528\u6237\u6709\u4e0b\u8f7d\u8981\u6c42\u65f6,\u4f18\u5148\u6267\u884c\u8be5\u51fd\u6570\u4e0b\u8f7d\u5bf9\u5e94\u7684\u8bba\u6587,\u65e0\u8bda\u6210\u4e0e\u5426,\u90fd\u5411\u7528\u6237\u53cd\u9988\u51fd\u6570\u7684return,\u82e5\u4e0b\u8f7d\u5f02\u5e38,\u518d\u8c03\u7528search_download\u8fdb\u884c\u5c1d\u8bd5"
)
def download_paper(
        target_num:int = Field(description = "\u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u6570\u91cf"),
        target_id:list = Field(description = "\u5f85\u4e0b\u8f7d\u8bba\u6587\u7684arxiv id\u7ec4\u6210\u7684\u5217\u8868"),
        file_type:str = Field(
            description = "\u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u683c\u5f0f,\u9ed8\u8ba4\u4e3aPDF,\u8fd8\u53ef\u4ee5\u9009\u62e9LaTeX\u683c\u5f0f",
            default = "PDF",
            json_schema_extra = {"enum":["PDF","LaTeX"]}
        ),
        dir:str = Field(
            description = "\u4e0b\u8f7d\u4fdd\u5b58\u7684\u5730\u5740",
            default = DOWNLOAD_PATH
        )
) -> DownloadSuccessResult|DownloadErrorResult:
    global PAPER_CACHE
    undo_ids = target_id
    if file_type not in ["PDF","LaTeX"]:
        return DownloadErrorResult(
            display_result = "error",
            message = "\u6682\u4e0d\u652f\u6301\u6b64\u79cd\u683c\u5f0f\u7684\u4e0b\u8f7d,\u7ed3\u675f\u4e0b\u8f7d\u4efb\u52a1",
            undo_ids = undo_ids
        )
    success_num = 0
    try:
        for arxiv_id in target_id:
            paper =  PAPER_CACHE.get(arxiv_id)
            if paper is not None:
                if file_type =="PDF":
                    paper.download_pdf(dir)
                else:
                    paper.download_source(dir)
                success_num = success_num + 1
                undo_ids.remove(arxiv_id)
       
        if len(undo_ids) > 0:
            return DownloadErrorResult(
                download_result = "error",
                message = f"\u7f13\u5b58\u4e2d\u672a\u67e5\u5230arxiv_id,\u4e0b\u8f7d\u672a\u5b8c\u6210,\u6700\u7ec8\u4e0b\u8f7d\u8fdb\u5ea6\u4e3a:{success_num}/{target_num}",
                undo_ids = undo_ids
            )
        else:
            return DownloadSuccessResult(
                download_result = "success",
                message = f"\u4e0b\u8f7d\u5b8c\u6210,\u4e0b\u8f7d\u603b\u91cf:{success_num},\u4fdd\u5b58\u4f4d\u7f6e：{dir}",
            )
    except Exception as e:
        return DownloadErrorResult(
            download_result = "error",
            message = f"\u4e0b\u8f7d\u62a5\u9519\uff1a{repr(e)},\u6700\u7ec8\u4e0b\u8f7d\u8fdb\u5ea6\u4e3a:{success_num}/{target_num}",
            undo_ids = undo_ids
        )

@mcp.tool(
    name="search_download",
    description="\u5f53download_paper\u6ca1\u6709\u5b8c\u6210\u4e0b\u8f7d\u4efb\u52a1\u65f6,\u5c06\u8fd4\u56de\u7684undo_ids\u4f20\u5165\u8be5\u51fd\u6570,\u91cd\u65b0\u67e5\u627e\u672a\u4e0b\u8f7d\u7684\u8bba\u6587\u8865\u5145\u4e0b\u8f7d,\u65e0\u8bda\u6210\u4e0e\u5426,\u90fd\u5411\u7528\u6237\u53cd\u9988\u51fd\u6570\u7684return"
)
def search_download(
    target_num:int = Field(description = "\u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u6570\u91cf"),
    undo_ids:list = Field(description = "\u672a\u5b8c\u6210\u4e0b\u8f7d\u7684\u8bba\u6587\u7684arxiv id\u7ec4\u6210\u7684\u5217\u8868"),
    file_type:str = Field(
        description = "\u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u683c\u5f0f,\u9ed8\u8ba4\u4e3aPDF,\u8fd8\u53ef\u4ee5\u9009\u62e9LaTeX\u683c\u5f0f",
        default = "PDF",
        json_schema_extra = {"enum":["PDF","LaTeX"]}
    ),
    dir:str =  Field(
            description = "\u4e0b\u8f7d\u4fdd\u5b58\u7684\u5730\u5740",
            default = DOWNLOAD_PATH
    )
) -> DownloadSuccessResult|DownloadErrorResult:
    if file_type not in ["PDF","LaTeX"]:
        return DownloadErrorResult(
            download_result = "error",
            message = "\u6682\u4e0d\u652f\u6301\u6b64\u79cd\u683c\u5f0f\u7684\u4e0b\u8f7d,\u7ed3\u675f\u4e0b\u8f7d\u4efb\u52a1",
            undo_ids = undo_ids
        )
    success_num = 0
    try:
        search = arxiv.Search(id_list = undo_ids)
        client = arxiv.Client()
        for paper in client.results(search):
            if file_type =="PDF":
                paper.download_pdf(dir)
            else:
                paper.download_source(dir)
            success_num = success_num + 1
            undo_ids.remove(paper.get_short_id())
       
        return DownloadSuccessResult(
            download_result = "success",
            message = f"\u4e0b\u8f7d\u5b8c\u6210,\u4e0b\u8f7d\u603b\u91cf:{success_num},\u4fdd\u5b58\u4f4d\u7f6e：{dir}"
        )
    except Exception as e:
        return DownloadErrorResult(
            download_result = "error",
            message = f"\u4e0b\u8f7d\u62a5\u9519\uff1a{repr(e)},\u6700\u7ec8\u4e0b\u8f7d\u8fdb\u5ea6\u4e3a:{success_num}/{target_num}",
            undo_ids = undo_ids
        )
     
if __name__ == "__main__":
    mcp.run(transport="stdio")