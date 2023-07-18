from deta import Deta

d = Deta("a0xztrxeaye_oCyrV2ZZAKZqn4fw7NEG8hhJdn56YMau")

drive = d.Drive("eng_simplified")

with open("../../wordsAPI/simplified_eng_dict.json", "r") as upload_fp:

    drive.put("simplified_eng_dict.json", upload_fp)