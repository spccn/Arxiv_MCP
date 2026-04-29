# arxiv_mcp

一个基于 arXiv 库的arXiv论文搜索与下载的MCP工具。

## 功能概述

提供三个核心MCP工具函数：

- **query_paper**: 根据关键词搜索 arXiv 论文
- **download_paper**: 下载论文（支持PDF 或 LaTeX格式）
- **search_download**: 补充下载（当 download_paper 缓存未命中时继续当前未完成的下载）

## 安装依赖

```bash
pip install fastmcp pydantic arxiv
```

## MCP接入配置（Opencode版）

修改 `opencode.json` 中的参数：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "arxiv_mcp": {
      "type": "local",
      "command": ["python.exe 解释器的绝对路径", "MCP代码arxiv_mcp.py 的绝对路径"],
      "enabled": true,
      "environment": {
        "DOWNLOAD_PATH": "论文默认保存位置的绝对路径"
      }
    }
  }
}
```

## MCP函数内容

### 1. query_paper

根据 query 语句搜索论文。

**参数：**
- `query`: 搜索关键词 / 表达式（支持 arXiv 原生检索语法）
  - 单关键词：`"transformer"`
  - 多条件：`"title:transformer AND author:attention"`
  - 列表形式：`["transformer", "attention"]`（OR 逻辑）
- `max_results`: 返回论文的最大数量（默认 5）
- `sort_by`: 排序规则
  - `arxiv.SortCriterion.Relevance`（相关性，默认）
  - `arxiv.SortCriterion.SubmittedDate`（提交时间）
  - `arxiv.SortCriterion.LastUpdatedDate`（最后更新时间）
- `sort_order`: 排序顺序
  - `arxiv.SortOrder.Descending`（降序）
  - `arxiv.SortOrder.Ascending`（升序）

**返回值：**
```python
{
    "id": "完整论文 ID(含版本号)",
    "title": "论文标题",
    "abstract": "论文摘要",
    "categories": ["cs.CL", "cs.LG"],
    "authors": ["作者1", "作者2"],
    "pdf_url": "https://arxiv.org/pdf/...",
    "publish_date": "2026-04-27 17:23:37+00:00",
    "journal_ref": None,
    "doi": None
}
```

### 2. download_paper

下载指定论文。

**参数：**
- `target_num`: 需要下载的论文数量
- `target_id`: 待下载论文的 arXiv ID 列表
- `file_type`: 下载格式（`"PDF"` 或 `"LaTeX"`，默认 `"PDF"`）
- `dir`: 保存路径（默认使用环境变量 `DOWNLOAD_PATH`）

**返回值：**
- 成功：
  ```python
  {
      "download_result": "success",
      "message": "下载完成,下载总量:1,保存位置：..."
  }
  ```
- 失败：
  ```python
  {
      "download_result": "error",
      "message": "错误信息",
      "undo_ids": ["未完成下载的 arXiv ID 列表"]
  }
  ```

### 3. search_download

当 `download_paper` 缓存未命中时，补充下载。

**参数：**
- `target_num`: 需要下载的论文数量
- `undo_ids`: 未完成下载的 arXiv ID 列表
- `file_type`: 下载格式
- `dir`: 保存路径

**返回值：** 同 `download_paper`

## 查询语法参考

| 字段 | 说明 |
|------|------|
| `ti` | 标题 |
| `au` | 作者 |
| `abs` | 摘要 |
| `cat` | 学科分类 |
| `doi` | DOI 号 |
| `all` | 匹配所有字段 |

**逻辑运算符：** `AND`, `OR`, `NOT`, `*`（通配符）

**示例：**
- `ti:LLM AND cat:cs.CL` - 查找标题含 LLM 的计算语言学论文
- `all:transformer` - 全字段搜索 transformer
- `submittedDate:[2024 TO 2025]` - 查找 2024-2025 年提交的论文

使用 `stdio` 传输协议，可直接与 MCP 客户端集成