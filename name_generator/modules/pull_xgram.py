#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json
from deta import Deta

d = Deta("a0xztrxeaye_oCyrV2ZZAKZqn4fw7NEG8hhJdn56YMau")

drive = d.Drive("eng_simplified")

reader = drive.get("xgrams.json")

x_grams: dict = json.loads(reader.read())