#!/usr/bin/env python3
# -*- coding:utf-8 -*- 
# Created by yaochao at 2018/3/8


import docx
import os
import re

base = '/Users/yaochao/test/doc_handle1'
files_name = os.listdir(base)


def get_all_texts():
    files = [os.path.join(base, x) for x in files_name]
    texts = []
    for f in files:
        if '.docx' in f:
            doc = docx.Document(f)
            paragraphs = doc.paragraphs
            text = '\n'.join([x.text for x in paragraphs])
            texts.append(text)
    return texts


def get_all_titles(texts):
    title_re = r'【.*?】'
    title_re = re.compile(title_re)
    titles = []
    for t in texts:
        r = re.findall(title_re, t)
        titles.extend(r)
    return set(titles)


def get_all_parts(titles, text):
    parts = []
    for title in titles:
        title_re = '(' + title + r'[\w\W]+?)\n【.*?】\n'
        part = re.findall(title_re, text)
        parts.append(part)
    return parts


def main():
    texts = get_all_texts()
    titles = get_all_titles(texts)
    for text in texts[:1]:
        parts = get_all_parts(titles, text)
        for part in parts:
            print(part)


if __name__ == '__main__':
    main()
