#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json
from deta import Deta

with open("name_generator/keys.json") as keys_files:
    keys_dict = json.loads(keys_files.read())
deta_key = keys_dict["deta_key"]

d = Deta(deta_key)
drive = d.Drive("eng_simplified")
reader = drive.get("simplified_eng_dict.json")
eng_dict: dict = json.loads(reader.read())