# 参考方案

入口文件，请参考`src/main.py`
```python
def main():
    # 公司名提取
    extract_company_names()
    # 问题类型分类
    split_questions_by_type()
    # 文本理解
    swifter_process_text_questions()
    # 数据查询
    swifter_process_data_questions()
    # 答案合并
    integrate_outputs()
```
解题思路如下： 

### Step 1: 题目分类

1. 基于千问模型，提取出80篇招股说明书所属公司，具体实现请参考`extract_company_names`；
2. 使用 `split_questions_by_type` 将1000道题目分成文本理解题和数据处理题两大类，以便后续分别设计不同解题思路。
   * 题目中主体公司为有招股说明书的公司，则分类为文本理解题，其余为信息提取题

### Step 2: 文本理解题处理

1. 问题分类后，基于问题中提及的公司和招股书文档进行对应，对文档进行chunk切分，检索问题最相关的文档chunk，设计prompt进行问题回答，具体实现，请参考`swifter_process_text_questions`函数。

### Step 3: 数据查询题处理

1. 设计prompt，千问模型生成相应的SQL语句
    * 对每一题，输入给千问模型10张表的表名字段名和少量数据样本，让千问回答解决问题的SQL语句
2. 针对qwen生成的回复，提取回答中的SQL语句，并基于规则的方式，进行进一步的refine；
3. 执行SQL语句得到得出数据库查询结果，并与问题一同输入千问模型，得到最终答案；

### Step 4: 合并整理数据查询题与文本理解题

1. 使用函数 `integrate_outputs`，最后输出结果。
