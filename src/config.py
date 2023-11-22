#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
def get_base_file_path():
    return os.path.dirname(os.path.dirname(__file__))

class Config:
    base_path = get_base_file_path()
    data_path = os.path.join(base_path, "data")
    text_files_path = os.path.join(data_path, "bs_challenge_financial_14b_dataset/pdf_txt_file").replace("\\", "/")
    db_sqlite_url = os.path.join(data_path, "bs_challenge_financial_14b_dataset/dataset/博金杯比赛数据.db").replace("\\", "/")

    save_path = os.path.join(data_path, "stock_descriptions/txtfile2company.csv").replace("\\", "/")

    questions_path = os.path.join(data_path, "bs_challenge_financial_14b_dataset/question.json").replace("\\", "/")
    company_file_path = os.path.join(data_path, "stock_descriptions/txtfile2company.csv").replace("\\", "/")
    text_questions_path = os.path.join(data_path, "sample_data/文本理解题.csv").replace("\\", "/")
    data_questions_path = os.path.join(data_path, "sample_data/数据查询题.csv").replace("\\", "/")

    text_answer_path = os.path.join(data_path, "sample_data/文本理解题答案.csv").replace("\\", "/")
    data_answer_path = os.path.join(data_path, "sample_data/数据查询题答案.csv").replace("\\", "/")

    answer_path = os.path.join(base_path, "answer.jsonl")


project_config = Config()
