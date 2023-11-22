#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import swifter

import pandas as pd
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from model.ai_loader import client
from utils import cosine_similarity
from config import project_config

def text_split(content):
    """ 将文本分割为较小的部分 """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=100,
        separators=['\n\n', "\n", "。"],
        keep_separator=False)
    return text_splitter.split_text(content)

def text_similarity(text, embedding):
    """ 计算文本和问题的相似度 """
    text_embedding = client.embeddings.create(input=[text], model='moka-ai/m3e-base').data[0].embedding
    return cosine_similarity(text_embedding, embedding)

def process_text_question(question, txtdf, text_files_path):
    """ 处理单个问题 """
    try:
        q = question['question']
        question_embedding = client.embeddings.create(input=[q], model='moka-ai/m3e-base').data[0].embedding

        company = question['company']
        file_name = txtdf.loc[txtdf['company'] == company]['filename'].values[0]
        file_path = os.path.join(text_files_path, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        text_list = text_split(content)
        sim_list = [text_similarity(text, question_embedding) for text in text_list]

        sorted_indices = sorted(enumerate(sim_list), key=lambda x: x[1], reverse=True)
        top_texts = [text_list[index] for index, _ in sorted_indices[:2]]

        prompt = ChatPromptTemplate.from_template(
            "你是一个能精准提取文本信息并回答问题的AI。\n"
            "请根据以下资料的所有内容，首先帮我判断能否依据给定材料回答出问题。"
            "如果能根据给定材料回答，则提取出最合理的答案来回答问题,并回答出完整内容，不要输出表格：\n\n"
            "{text}\n\n"
            "请根据以上材料回答：{q}\n\n"
            "请按以下格式输出：\n"
            "能否根据给定材料回答问题：回答能或否\n"
            "答案：").format_messages(q=q, text="\n".join(top_texts))

        response = client.chat.completions.create(model="Tongyi-Finance-14B-Chat", messages=[{"role": "user", "content": prompt[0].content}], temperature=0.01, top_p=0.5)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing question: {e}")
        return None

def swifter_process_text_questions():
    questions_df = pd.read_csv(project_config.text_questions_path,index_col=0)
    txtdf = pd.read_csv(project_config.company_file_path)
    text_files_path = project_config.text_files_path
    # 使用swifter加速apply操作
    questions_df['answer'] = questions_df.swifter.apply(lambda x: process_text_question(x, txtdf, text_files_path), axis=1)
    # questions_df['answer'] = questions_df.apply(lambda x: process_text_question(x, txtdf, text_files_path), axis=1)
    questions_df.to_csv(project_config.text_answer_path)


