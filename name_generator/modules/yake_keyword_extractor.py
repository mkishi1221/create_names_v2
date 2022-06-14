#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import yake
import orjson as json

def keyword_extractor(output_fp: str, sentences: str = None, keywords: list = None):

    if keywords == None:
        text = sentences
    elif sentences == None:
        text = ", ".join(keywords)
    elif sentences != None and keywords != None:
        text = ", ".join(keywords) + "\n\n" + sentences
    else:
        print("No text found!")
        text = None

    if text is not None:
        language = "en"
        max_ngram_size = 1
        deduplication_thresold = 0.9
        deduplication_algo = 'seqm'
        windowSize = 1
        numOfKeywords = 1000
        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
        ranked_keywords_list = custom_kw_extractor.extract_keywords(text)

        ranked_keywords = {}
        for index, kw in enumerate(ranked_keywords_list):
            ranked_keywords[kw[0].lower()]= (index + 1, str(kw[1]))

    else:
        ranked_keywords = None

    with open(output_fp, "wb+") as out_file:
        out_file.write(json.dumps(ranked_keywords, option=json.OPT_INDENT_2))
    
    return ranked_keywords

