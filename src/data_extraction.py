#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 14:21
# @Author  : renyx
# @File    : data_extraction.py
# @Software: PyCharm

import pandas as pd
import sqlite3
from langchain.prompts import ChatPromptTemplate
from langchain.utilities import SQLDatabase
from model.ai_loader import client
from config import project_config
import swifter  # 引入swifter

def create_sql_template():
    return ChatPromptTemplate.from_template(
        "你是一个精通SQL语句的AI。"
        "我会给你一个问题，请按照问题描述，只使用以下表格的表格名和列名写出正确的SQL代码，（数据只是样本，不代表数据库内所有数据，请按照具体问题的主体和要对应表名和字段名撰写SQL语句）。\n"
        "请直接生成能在以下数据库中执行成功的SQL代码,不要有多余备注和假设。\n"
        "请只使用以下表格的表格名和列名撰写SQL语句：\n\n"
        "{db}\n\n"
        "问题：{q}\n"
        "SQL语句：\n"
    )
def create_answer_template():
    return ChatPromptTemplate.from_template(
        "你是一个会组织语言的AI。"
        "我会给你一个问题，和相应的答案，请为我完整写出答案句\n"
        "问题：{q}\n"
        "答案：{a}\n"
        "答案句为："
    )
# 获取SQL回答
def get_sql_answer(template, db, question):
    prompt = template.format_messages(q=question, db=db.table_info)
    resp = client.chat.completions.create(model="Tongyi-Finance-14B-Chat", messages=[{"role": "user", "content": prompt[0].content}], temperature=0.7, top_p=0.5)
    # print(resp.choices[0].message.content)
    return resp.choices[0].message.content


# 处理SQL答案
def process_sql_answer(answer):
    try:
        ind = answer.index("SELECT")
        answer = answer[ind:]
        ind = answer.index(';')
        answer = answer[:ind + 1]
    except ValueError:
        pass

    # 去除引号
    if answer[0] in ['"', "'"]:
        answer = answer[1:]
    if answer[-1] == '"':
        answer = answer[:-1]
    if answer[-1] != ';':
        answer += ';'

    # 进行字符串替换
    answer = answer.replace('`',"'")
    answer = answer.replace("\n"," ")

    answer = answer.replace("昨收盘(元)", "昨收盘")
    answer = answer.replace("今开盘(元)", "今开盘")
    answer = answer.replace("最高价(元)", "最高价")
    answer = answer.replace("最低价(元)", "'最低价")
    answer = answer.replace("收盘价(元)", "收盘价")
    answer = answer.replace("成交量(股)", "成交量")
    answer = answer.replace("成交金额(元)", "成交金额")
    answer = answer.replace("所属国家(地区)", "所属国家")

    answer = answer.replace("昨收盘","昨收盘(元)")
    answer = answer.replace("今开盘", "今开盘(元)")
    answer = answer.replace("最高价", "最高价(元)")
    answer = answer.replace("最低价", "'最低价(元)")
    answer = answer.replace("收盘价", "收盘价(元)")
    answer = answer.replace("成交量", "成交量(股)")
    answer = answer.replace("成交金额", "成交金额(元)")
    answer = answer.replace("所属国家", "所属国家(地区)")

    answer = answer.replace("'昨收盘(元)'","昨收盘(元)")
    answer = answer.replace("'今开盘(元)'", "今开盘(元)")
    answer = answer.replace("'最高价(元)'", "最高价(元)")
    answer = answer.replace("'最低价(元)'", "最低价(元)")
    answer = answer.replace("'收盘价(元)'", "收盘价(元)")
    answer = answer.replace("'成交量(股)'", "成交量(股)")
    answer = answer.replace("'成交金额(元)'", "成交金额(元)")
    answer = answer.replace("'所属国家(地区)'", "所属国家(地区)")

    answer = answer.replace("昨收盘(元)","'昨收盘(元)'")
    answer = answer.replace("今开盘(元)", "'今开盘(元)'")
    answer = answer.replace("最高价(元)", "'最高价(元)'")
    answer = answer.replace("最低价(元)", "'最低价(元)'")
    answer = answer.replace("收盘价(元)", "'收盘价(元)'")
    answer = answer.replace("成交量(股)", "'成交量(股)'")
    answer = answer.replace("成交金额(元)", "'成交金额(元)'")
    answer = answer.replace("所属国家(地区)", "'所属国家(地区)'")

    return answer

# 获取格式化的答案
def get_formatted_answer(template, question, answer):
    prompt = template.format_messages(q=question, a=answer)
    resp = client.chat.completions.create(model="Tongyi-Finance-14B-Chat", messages=[{"role": "user", "content": prompt[0].content}], temperature=0.1, top_p=0.5)
    return resp.choices[0].message.content
# 执行SQL查询并获取结果
def execute_sql_query(conn, query):
    try:
        result = conn.execute(query).fetchone()
        return ', '.join(map(str, result)) if result else ''
    except Exception as e:
        return str(e)  # 或者返回空字符串
def swifter_process_data_questions():
    db = SQLDatabase.from_uri("sqlite:///"+ project_config.db_sqlite_url, sample_rows_in_table_info=2)
    sql_template = create_sql_template()
    answer_template = create_answer_template()
    questions = pd.read_csv(project_config.data_questions_path,index_col=0)
    # 使用swifter加速处理
    # questions['answer'] = questions.swifter.apply(lambda row: process_sql_answer(get_sql_answer(sql_template, db, row['question'])), axis=1)
    questions['answer'] = questions.apply(lambda row: process_sql_answer(get_sql_answer(sql_template, db, row['question'])), axis=1)

    # 连接数据库
    conn = sqlite3.connect(project_config.db_sqlite_url)
    output = pd.DataFrame(columns=['id', 'question', 'formatted_answer'])

    for i, row in questions.iterrows():
        sql_result = execute_sql_query(conn, row['answer'])
        formatted_answer = get_formatted_answer(answer_template, row['question'], sql_result)
        output.at[i, 'id'] = row['id']
        output.at[i, 'question'] = row['question']
        output.at[i, 'formatted_answer'] = formatted_answer

    output.to_csv(project_config.data_answer_path)


if __name__ == '__main__':
    swifter_process_data_questions()
