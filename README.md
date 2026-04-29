# arxiv_mcp

\u4e00\u4e2a\u57fa\u4e8e arXiv \u5e93\u7684arXiv\u8bba\u6587\u641c\u7d22\u4e0e\u4e0b\u8f7d\u7684MCP\u5de5\u5177\u3002

\u529f\u80fd\u6982\u8ff0

\u63d0\u4f9b\u4e09\u4e2a\u6838\u67b6MCP\u5de5\u5177\u51fd\u6570\uff1a

- **query_paper**: \u6839\u636e\u5173\u952e\u8bcd\u641c\u7d22 arXiv \u8bba\u6587
- **download_paper**: \u4e0b\u8f7d\u8bba\u6587\uff08\u652f\u6301PDF \u6216 LaTeX\u683c\u5f0f\uff09
- **search_download**: \u8865\u5145\u4e0b\u8f7d\uff08\u5f53 download_paper \u7f13\u5b58\u672a\u547d\u4e2d\u65f6\u7ee7\u7eed\u5f53\u524d\u672a\u5b8c\u6210\u7684\u4e0b\u8f7d\uff09

\u5b89\u88c5\u4f9d\u8d28

```bash
pip install fastmcp pydantic arxiv
```

MCP\u63a5\u5165\u914d\u7f6e\uff08Opencode\u7248\uff09

\u4fee\u6539 `opencode.json` \u4e2d\u7684\u53c2\u6570\uff1a

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "arxiv_mcp": {
      "type": "local",
      "command": ["python.exe \u89e3\u91cb\u5668\u7684\u7edd\u5bf9\u8def\u5f91", "MCP\u4ee3\u7801arxiv_mcp.py \u7684\u7edd\u5bf9\u8def\u5f91"],
      "enabled": true,
      "environment": {
        "DOWNLOAD_PATH": "\u8bba\u6587\u9ed8\u8ba4\u4fdd\u5b58\u4f4d\u7f6e\u7684\u7edd\u5bf9\u8def\u5f91"
      }
    }
  }
}
```

MCP\u51fd\u6570\u5185\u5bb9

### 1. query_paper

\u6839\u636e query \u8bed\u53e5\u641c\u7d22\u8bba\u6587\u3002

\u53c2\u6570\uff1a
- `query`: \u641c\u7d22\u5173\u952e\u8bcd / \u8868\u8fbe\u5f0f\uff08\u652f\u6301 arXiv \u539f\u751f\u68c0\u7d22\u8bed\u6cd5\uff09
  - \u5355\u5173\u952e\u8bcd\uff1a`\"transformer\"`
  - \u591a\u6761\u4ef6\uff1a`\"title:transformer AND author:attention\"`
  - \u5217\u8868\u5f62\u5f0f\uff1a`[\"transformer\", \"attention\"]`\uff08OR \u903b\u8f91\uff09
- `max_results`: \u8fd4\u8bba\u6587\u7684\u6700\u5927\u6570\u91cf\uff08\u9ed8\u8ba4 5\uff09
- `sort_by`: \u6392\u5e8f\u89c4\u5219
  - `arxiv.SortCriterion.Relevance`\uff08\u76f8\u5173\u6027\uff0c\u9ed8\u8ba4\uff09
  - `arxiv.SortCriterion.SubmittedDate`\uff08\u63d0\u4ea4\u65f6\u95f4\uff09
  - `arxiv.SortCriterion.LastUpdatedDate`\uff08\u6700\u540e\u66f4\u65b0\u65f6\u95f4\uff09
- `sort_order`: \u6392\u5e8f\u987a\u5e8f
  - `arxiv.SortOrder.Descending`\uff08\u964d\u5e8f\uff09
  - `arxiv.SortOrder.Ascending`\uff08\u5347\u5e8f\uff09

\u8fd4\u56de\u503c\uff1a
```python
{
    "id": "\u5b8c\u6574\u8bba\u6587 ID(\u542b\u7248\u672c\u53f7)",
    "title": "\u8bba\u6587\u6807\u9898",
    "abstract": "\u8bba\u6587\u6458\u8981",
    "categories": ["cs.CL", "cs.LG"],
    "authors": ["\u4f5c\u80051", "\u4f5c\u80052"],
    "pdf_url": "https://arxiv.org/pdf/...",
    "publish_date": "2026-04-27 17:23:37+00:00",
    "journal_ref": None,
    "doi": None
}
```

### 2. download_paper

\u4e0b\u8f7d\u6307\u5b9a\u8bba\u6587\u3002

\u53c2\u6570\uff1a
- `target_num`: \u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u6570\u91cf
- `target_id`: \u5f85\u4e0b\u8f7d\u8bba\u6587\u7684 arXiv ID \u5217\u8868
- `file_type`: \u4e0b\u8f7d\u683c\u5f0f\uff08`\"PDF\"` \u6216 `\"LaTeX\"`\uff0c\u9ed8\u8ba4 `\"PDF\"`\uff09
- `dir`: \u4fdd\u5b58\u8def\u5f91\uff08\u9ed8\u8ba4\u4f7f\u7528\u73af\u5883\u53d8\u91cf `DOWNLOAD_PATH`\uff09

\u8fd4\u56de\u503c\uff1a
- \u6210\u529f\uff1a
  ```python
  {
      "download_result": "success",
      "message": "\u4e0b\u8f7d\u5b8c\u6210,\u4e0b\u8f7d\u603b\u91cf:1,\u4fdd\u5b58\u4f4d\u7f6e\uff1a..."
  }
  ```
- \u5931\u8d25\uff1a
  ```python
  {
      "download_result": "error",
      "message": "\u9519\u8bef\u4fe1\u606f",
      "undo_ids": ["\u672a\u5b8c\u6210\u4e0b\u8f7d\u7684 arXiv ID \u5217\u8868"]
  }
  ```

### 3. search_download

\u5f53 `download_paper` \u7f13\u5b58\u672a\u547d\u4e2d\u65f6\uff0c\u8865\u5145\u4e0b\u8f7d\u3002

\u53c2\u6570\uff1a
- `target_num`: \u9700\u8981\u4e0b\u8f7d\u7684\u8bba\u6587\u6570\u91cf
- `undo_ids`: \u672a\u5b8c\u6210\u4e0b\u8f7d\u7684\u8bba\u6587\u7684 arXiv ID \u5217\u8868
- `file_type`: \u4e0b\u8f7d\u683c\u5f0f
- `dir`: \u4fdd\u5b58\u8def\u5f91

\u8fd4\u56de\u503c\uff1a \u540c `download_paper`

\u67e5\u8be2\u8bed\u6cd5\u53c2\u8003

| \u5b57\u6bb5 | \u8bf4\u660e |
|------|------|
| `ti` | \u6807\u9898 |
| `au` | \u4f5c\u8005 |
| `abs` | \u6458\u8981 |
| `cat` | \u5b66\u79d1\u5206\u7c7b |
| `doi` | DOI \u53f7 |
| `all` | \u5339\u914d\u6240\u6709\u5b57\u6bb5 |

\u903b\u8f91\u8fd0\u7b97\u7b5c\uff1a`AND`, `OR`, `NOT`, `*`\uff08\u901a\u914d\u7b26\uff09

\u793a\u4f8b\uff1a
- `ti:LLM AND cat:cs.CL` - \u67e5\u627e\u6807\u9898\u542b LLM \u7684\u8ba1\u7b97\u8bed\u8a00\u5b66\u8bba\u6587
- `all:transformer` - \u5168\u5b57\u6bb5\u641c\u7d22 transformer
- `submittedDate:[2024 TO 2025]` - \u67e5\u627e 2024-2025 \u5e74\u63d0\u4ea4\u7684\u8bba\u6587

\u4f7f\u7528 `stdio` \u4f20\u8f93\u534f\u8bae\uff0c\u53ef\u76f4\u63a5\u4e0e MCP \u5ba2\u6237\u7aef\u96c6\u6210\u3002