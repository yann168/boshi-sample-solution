#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.ai_loader import client
from langchain.prompts import ChatPromptTemplate
from utils import read_jsonl
from config import project_config
import pandas as pd
import os


def extract_company_names():
    df = pd.DataFrame(columns=['filename', 'company'])
    i = 1
    for filename in os.listdir(project_config.text_files_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(project_config.text_files_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                template = ChatPromptTemplate.from_template(
                    "你是一个能精准提取信息的AI。"
                    "我会给你一篇招股说明书，请输出此招股说明书的主体是哪家公司，若无法查询到，则输出无。\n"
                    "{t}\n\n"
                    "请指出以上招股说明书属于哪家公司，请只输出公司名。"
                )
                prompt = template.format_messages(t=content[:3000])
                resp = client.chat.completions.create(model="Tongyi-Finance-14B-Chat",
                                                      messages=[{"role": "user", "content": prompt[0].content}],
                                                      temperature=0.1, top_p=0.5)
                result = resp.choices[0].message.content
                df.at[i, 'filename'] = filename
                df.at[i, 'company'] = result
                i += 1
    df.to_csv(project_config.save_path)


def split_questions_by_type():
    questions = read_jsonl(project_config.questions_path)
    df = pd.read_csv(project_config.company_file_path)
    company_list = df['company']

    df_text = pd.DataFrame(columns=['id', 'question', 'company'])
    df_data = pd.DataFrame(columns=['id', 'question'])
    i_text, i_data = 0, 0

    for question in questions:
        flag = True
        q = question['question']
        for company in company_list:
            if company in q:
                df_text.at[i_text, 'id'] = question['id']
                df_text.at[i_text, 'question'] = question['question']
                df_text.at[i_text, 'company'] = company
                flag = False
                i_text += 1
                break
        if flag:
            df_data.at[i_data, 'id'] = question['id']
            df_data.at[i_data, 'question'] = question['question']
            i_data += 1

    df_text.to_csv(project_config.text_questions_path)
    df_data.to_csv(project_config.data_questions_path)
