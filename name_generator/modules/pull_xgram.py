#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json
from deta import Deta

def pull_xgrams():
    print("Pulling xgrams from deta...")
    with open("name_generator/keys.json") as keys_files:
        keys_dict = json.loads(keys_files.read())
    deta_key = keys_dict["deta_key"]

    d = Deta(deta_key)
    drive = d.Drive("xgrams")
    reader = drive.get("xgrams.json")
    x_grams: dict = json.loads(reader.read())
    return x_grams