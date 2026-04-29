from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel,Field
import arxiv
import os

mcp = FastMCP()

DOWNLOAD_PATH: str =  os.getenv("DOWNLOAD_PATH")
PAPER_CACHE: dict[str:arxiv.Result] = {}

class PaperInfo(BaseModel):
    id:str = Field(description ="完整论文 ID(含版本号)")
    title:str = Field(description = "论文标题")
    abstract:str = Field(description = "论文摘要")
    categories: list[str] = Field(description = "论文的arXiv分类列表")
    authors: list[str] = Field(description = "论文作者列表")
    pdf_url: str|None = Field(description = "论文PDF访问链接")
    publish_date: str = Field(description = "论文首次提交时间(UTC时区)")
    journal_ref: str|None = Field(description ="期刊引用信息")
    doi: str|None = Field(description = "doi编号")

class QueryErrorResult(BaseModel):
    query:str = Field(description = "输入的查询语句")
    error_info:str = Field(description = "报错信息")

class DownloadSuccessResult(BaseModel):
    download_result:str = Field(description = "下载结果")
    message:str = Field(description = "下载成功的补充信息")

class DownloadErrorResult(BaseModel):
    download_result:str = Field(description = "下载结果")
    message:str = Field(description = "下载失败的补充信息")
    undo_ids:list[str] = Field(description = "下载失败的论文的arxiv id列表 ")

@mcp.tool(
    name="query_paper",
    description="根据生成的query语句搜索arXiv论文,根据用户意图返回相关论文信息,如查询中出现异常,需向用户提供查询的return"
)
def query_paper(
    query:str|list[str] = Field(
        description = """
            搜索关键词 / 表达式（支持 arXiv 原生检索语法） 
            - 单关键词："transformer"
            - 多条件："title:transformer AND author:attention"
            - 列表形式：["transformer", "attention"]（多关键词 OR 逻辑）
            """,
        examples = ["transformer","title:transformer AND author:attention",["transformer", "attention"]]
    ), 
    max_results:int = Field(
        description = "返回论文的最大数量",
        default = 5
    ),
    sort_by:arxiv.SortCriterion = Field(
        description = 
        """
            对结果排序的规则,可选值：
            - arxiv.SortCriterion.Relevance(相关性，默认)
            - arxiv.SortCriterion.SubmittedDate(提交时间，最新优先)
            - arxiv.SortCriterion.LastUpdatedDate(最后更新时间)
        """,
        default = arxiv.SortCriterion.Relevance,
        json_schema_extra= {"enum":[arxiv.SortCriterion.Relevance,arxiv.SortCriterion.SubmittedDate,arxiv.SortCriterion.LastUpdatedDate]}
    ),
    sort_order:arxiv.SortOrder = Field(
        description = 
        """
            排序顺序，可选值：
            - arxiv.SortOrder.Descending(降序)
            - arxiv.SortOrder.Ascending(升序)
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
    description="当用户有下载要求时,优先执行该函数下载对应的论文,无论成功与否,都向用户反馈函数的return,若下载异常,再调用search_download进行尝试"
)
def download_paper(
        target_num:int = Field(description = "需要下载的论文数量"),
        target_id:list = Field(description = "待下载论文的arxiv id组成的列表"),
        file_type:str = Field(
            description = "需要下载的论文格式,默认为PDF,还可以选择LaTeX格式",
            default = "PDF",
            json_schema_extra = {"enum":["PDF","LaTeX"]}
        ),
        dir:str = Field(
            description = "下载保存的地址",
            default = DOWNLOAD_PATH
        )
) -> DownloadSuccessResult|DownloadErrorResult:
    global PAPER_CACHE
    undo_ids = target_id
    if file_type not in ["PDF","LaTeX"]:
        return DownloadErrorResult(
            download_result = "error",
            message = "暂不支持此种格式的下载,终止下载任务",
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
                message = f"缓存中未查到arxiv_id,下载未完成,最终下载进度为:{success_num}/{target_num}",
                undo_ids = undo_ids
            )
        else:
            return DownloadSuccessResult(
                download_result = "success",
                message = f"下载完成,下载总量:{success_num},保存位置：{dir}",
            )
    except Exception as e:
        return DownloadErrorResult(
            download_result = "error",
            message = f"下载报错：{repr(e)},最终下载进度为:{success_num}/{target_num}",
            undo_ids = undo_ids
        )

@mcp.tool(
    name="search_download",
    description="当download_paper没有完成下载任务时,将返回的undo_ids传入该函数,重新查找未下载的论文补充下载,无论成功与否,都向用户反馈函数的return"
)
def search_download(
    target_num:int = Field(description = "需要下载的论文数量"),
    undo_ids:list = Field(description = "待下载论文的arxiv id组成的列表"),
    file_type:str = Field(
        description = "需要下载的论文格式,默认为PDF,还可以选择LaTeX格式",
        default = "PDF",
        json_schema_extra = {"enum":["PDF","LaTeX"]}
    ),
    dir:str =  Field(
            description = "下载保存的地址",
            default = DOWNLOAD_PATH
    )
) -> DownloadSuccessResult|DownloadErrorResult:
    if file_type not in ["PDF","LaTeX"]:
        return DownloadErrorResult(
            download_result = "error",
            message = "暂不支持此种格式的下载,终止下载任务",
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
            message = f"下载完成,下载总量:{success_num},保存位置：{dir}"
        )
    except Exception as e:
        return DownloadErrorResult(
            download_result = "error",
            message = f"下载报错：{repr(e)},最终下载进度为:{success_num}/{target_num}",
            undo_ids = undo_ids
        )
     
if __name__ == "__main__":
    mcp.run(transport="stdio")