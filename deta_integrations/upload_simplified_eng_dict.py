from deta import Deta
import orjson as json

with open("name_generator/keys.json") as keys_files:
    keys_dict = json.loads(keys_files.read())

    deta_key = keys_dict["deta_key"]
    print(deta_key)

d = Deta(deta_key)
drive = d.Drive("eng_simplified")

with open("../wordsAPI/simplified_eng_dict.json", "r") as upload_fp:
    drive.put("simplified_eng_dict.json", upload_fp)

