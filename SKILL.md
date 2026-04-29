---
name: arXiv-query语句规则
description: 当调用query_paper函数查询arXiv数据库时，根据用户输入和query规则为query_paper函数生成的query参数
---
1.**query支持的查询字段**
字段：关键词
ti: 标题
au: 作者
abs: 摘要
cat: 学科分类
jr: 期刊引用
doi: DOI号
id: arXiv论文ID
co: 备注/页数/投稿信息
submittedDate: 首次提交/发布时间 （YYYYMMDDHHMM：精确到分钟，必须使用GMT） 或 （YYYYMMDD：仅精确到天。系统通常会自动补充为“从当天00:00到23:59”）
updatedDate: 最后更新时间 （YYYYMMDDHHMM：精确到分钟，必须使用GMT） 或 （YYYYMMDD：仅精确到天。系统通常会自动补充为“从当天00:00到23:59”）
all: 匹配所有字段

2.**逻辑运算符**
AND 同时满足
OR 满足其一
NOT 排除
"" 精确短语匹配
* 通配符
() 括号改变优先级

3.**query示例**
<1> ti:LLM AND cat:cs.* AND submittedDate:[2024 TO 2025] -> 查询2024年到2025年中标题含有LLM的计算机领域下的所有子领域的论文
<2> all:transformer -> 等价于(ti:transformer OR abs:transformer OR au:transformer OR cat:transformer OR co:transformer OR jr:transformer OR rn:transformer)
<3> (ti:attention OR ti:transformer) AND (cat:cs.CL OR cat:cs.LG OR cat:cs.AI) AND submittedDate:[202401010000 TO 202412312359] -> 查询2024年全年提交的、标题包含"attention"或"transformer"、且属于计算语言学/机器学习/人工智能领域的论文
<4> cat:cs.CV AND submittedDate:[000000000000 TO 202201010000] -> 查询2022年之前计算机视觉领域的论文
<5> ti:"deep learning" ANDNOT au:"Geoffrey Hinton" -> 查找关于深度学习的论文，但排除 Geoffrey Hinton 作为作者的论文
