import orjson as json
from deta import Deta

with open("name_generator/keys.json") as keys_files:
    keys_dict = json.loads(keys_files.read())
deta_key = keys_dict["deta_key"]

d = Deta(deta_key)
domain_log_base = d.Base("domain_log")
domain_log_drive = d.Drive("domain_log")

def sync_logs():
    # get all entries of base
    response = domain_log_base.fetch()
    last = response.last
    entries = response.items

    while last is not None:
        response = domain_log_base.fetch(last=last)
        last = response.last
        entries += response.items

    # upload the results
    domain_log_drive.delete("domain_log.json")
    domain_log_drive.put("domain_log.json", json.dumps(list(map(lambda x: x["domain"], entries))))