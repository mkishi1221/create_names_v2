#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def pull_master_exempt():
    master_exempt_cw_txt_fp = "name_generator/master_exempt_contained_words.txt"
    master_exempt_contained_words = set(open(master_exempt_cw_txt_fp, "r").read().splitlines())
    return master_exempt_contained_words