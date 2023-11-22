#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/your/file/path')

from processing import extract_company_names, split_questions_by_type
from text_understanding import swifter_process_text_questions
from data_extraction import swifter_process_data_questions
import pandas as pd
from config import project_config
import json

def integrate_outputs():
    # 读取文本理解和数据查询的答案文件
    data = []
    i = 0
    i1 = 0
    i2 = 0
    df1 = pd.read_csv(project_config.text_answer_path,index_col=0)[['id', 'question', 'answer']]
    df2 = pd.read_csv(project_config.data_answer_path,index_col=0)[['id', 'question', 'formatted_answer']]
    df2.columns = ['id', 'question', 'answer']
    #print(df1.columns)
    #print(df2.columns)

    while i < 999:
        try:
            element = {}
            element['id'] = i
            if i == df1.at[i1, 'id']:
                element['question'] = df1.at[i1, 'question']
                element['answer'] = df1.at[i1, 'answer']
                i1 += 1
            if i == df2.at[i2, 'id']:
                element['question'] = df2.at[i2, 'question']
                element['answer'] = df2.at[i2, 'answer']
                i2 += 1
            i += 1
            data.append(element)
        except:
            break
    #print(data)
    with open(project_config.answer_path, 'w', encoding='utf-8') as file:
        for record in data:
            #print(record)
            json_record = json.dumps(record, ensure_ascii=False)
            file.write(json_record)
            file.write('\n')

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
if __name__ == "__main__":
    main()
