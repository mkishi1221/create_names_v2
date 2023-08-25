#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.domain_class import Domain, NameDomain
from classes.name_class import Graded_name
from modules.get_whois import get_whois, DomainStates
import sys
import orjson as json
import pandas as pd
from datetime import datetime
from typing import List
import os
import copy
from deta import Deta
from modules.domain_log_sync import sync_logs


with open("name_generator/keys.json") as keys_files:
    keys_dict = json.loads(keys_files.read())
deta_key = keys_dict["deta_key"]
d = Deta(deta_key)
domain_log_base = d.Base("domain_log")
domain_log_drive = d.Drive("domain_log")

checked_domains = json.loads(domain_log_drive.get("domain_log.json").read())


def create_NameDomain_obj(name_data: Graded_name, avail_domain_list: List[Domain], not_avail_domain_list: List[Domain]):
    return NameDomain (
        name_in_title=name_data.name_in_title,
        name_in_lower=name_data.name_in_lower,
        name_type=name_data.name_type,
        length=name_data.length,
        phonetic_score=name_data.phonetic_score,
        lowest_phonetic=name_data.lowest_phonetic,
        keywords=name_data.keywords,
        keyword_combinations=name_data.keyword_combinations,
        pos_combinations=name_data.pos_combinations,
        modifier_combinations=name_data.modifier_combinations,
        etymologies=name_data.etymologies,
        avail_domains=avail_domain_list,
        not_avail_domains=not_avail_domain_list,
        grade=name_data.grade,
    )

def create_excel_domain(name_type, status, data: NameDomain, domain:Domain, excel_domains):

    keyword_combinations = data.keyword_combinations

    kw = {
        "k1":[],
        "k2":[],
        "k3":[]
    }

    for kc in keyword_combinations:
        kc: str
        kw_list = kc.split("|")
        kw["k1"].append(kw_list[0])
        if len(kw_list) > 1:
            kw["k2"].append(kw_list[1])
        if len(kw_list) > 2:
            kw["k3"].append(kw_list[2])
    
    for key, value in kw.items():
        if len(value) == 0:
            kw[key] = None
        else:
            kw[key] = "|".join(set(value))

    excel_domain = {
        "name_in_lower": data.name_in_lower,
        "name_in_title": data.name_in_title,
        "domain": domain.domain,
        "length": data.length,
        "keyword_1":kw["k1"],
        "keyword_2":kw["k2"],
        "keyword_3":kw["k3"],
        "keywords": data.keywords,
        "keyword_combinations": keyword_combinations,
        "pos_combinations": data.pos_combinations,
        "modifier_combinations": data.modifier_combinations,
        "phonetic_score": data.phonetic_score,
        "lowest_phonetic": data.lowest_phonetic,
        "etymologies": data.etymologies,
        "grade": data.grade,
        "last_checked": datetime.fromtimestamp(domain.last_checked).strftime("%d-%b-%Y (%H:%M:%S)"),
        "data_valid_till": datetime.fromtimestamp(domain.data_valid_till).strftime("%d-%b-%Y (%H:%M:%S)"),
        "availability": domain.availability,
        "shortlist": domain.shortlist,
    }
    excel_domains[name_type][status].append(excel_domain)
    return excel_domains

def scrub_domain_log():
    fetch_query = {"data_valid_till?lt": int(datetime.now().timestamp())}
    response = domain_log_base.fetch(fetch_query)

    last = response.last
    values = response.items

    while response.last is not None:
        response = domain_log_base.fetch(fetch_query, last=last)
        last = response.last
        values += response.items

    for val in values:
        domain_log_base.delete(val["key"])

# Checks domain availability using whois
def check_domains(project_id: str, limit: int):

    scrub_domain_log()

    project_path = f"projects/{project_id}"

    # input file filepaths and filenames:
    sl_namelist_fp: str = f"{project_path}/tmp/name_generator/{project_id}_names_shortlist.json"

    # tmp file filepaths and filenames:
    json_output_fp: str = f"{project_path}/tmp/domain_checker/{project_id}_domains.json"
    json_ndl_output_fp = f"{project_path}/tmp/domain_checker/{project_id}_namedomain_list_domains.json"
    remaining_names_fp = f"{project_path}/tmp/domain_checker/{project_id}_remaining_name_shortlist.json"

    # output filepaths and filenames:
    excel_output_fp = f"{project_path}/results/{project_id}_domains.xlsx"

    limit = int(limit)

    # Open file with generated names
    if os.path.exists(remaining_names_fp):
        with open(remaining_names_fp, "rb") as namelist_file:
            names_dict = json.loads(namelist_file.read())
        k_list = list(names_dict.keys())
        for k in k_list:
            if k.endswith("_reject"):
                del names_dict[k]
        remaining = sum([len(names_dict[name_type]) for name_type in names_dict.keys()])
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"No new names detected. {remaining} names remaining...")

    else:
        with open(sl_namelist_fp, "rb") as namelist_file:
            names_dict = json.loads(namelist_file.read())
        k_list = list(names_dict.keys())
        for k in k_list:
            if k.endswith("_reject"):
                del names_dict[k]
        del names_dict["shortlisted keywords"]
        del names_dict["keyword_combinations"]
        del names_dict["statistics"]
        remaining = sum([len(names_dict[name_type]) for name_type in names_dict.keys()])
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"New names detected. Using {remaining} new names...")

    name_types = ["no_cut_name", "mspl_name", "text_comp_name", "fun_name", "pref_suff_name", "fit_name", "part_cut_name", "cut_name", "repeating_name"]
    NameDomain_dict = {}
    for name_type in name_types:
        NameDomain_dict[name_type] = {}
    if os.path.exists(json_output_fp):
        print("Previous domain check detected. Continuing domain check...")
        with open(json_output_fp, "rb") as NameDomain_file:
            NameDomain_dict_raw: dict = json.loads(NameDomain_file.read())
        name_list: dict
        for name_type, name_list in NameDomain_dict_raw.items():
            if not name_type.endswith("_reject"):
                for name_in_title, data in name_list.items():
                    avail_domains_list = []
                    for domain_obj in data["avail_domains"]:
                        avail_domains_list.append(Domain(**domain_obj))
                    not_avail_domains_list = []
                    for domain_obj in data["not_avail_domains"]:
                        not_avail_domains_list.append(Domain(**domain_obj))
                    data = copy.deepcopy(data)
                    data["avail_domains"] = avail_domains_list
                    data["not_avail_domains"] = not_avail_domains_list
                    NameDomain_dict[name_type][name_in_title] = NameDomain(**data)

    tld_list = [".com", ".co.uk"] #TODO: Change to file source ".co.uk", ".org", ".io" 

    json_ndl_output_fp = json_output_fp.replace("tmp/domain_checker/", "tmp/domain_checker/namedomain_list_")
    with open(json_ndl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    counter = 0
    all_available = 0
    for name_type in names_dict.keys():

        print(f"Checking domains for {name_type}s...")
        name_list = list(names_dict[name_type].keys())
        available = 0
        domain_log_use = ""

        # Check the shortest names from top of the name list until it reaches the desired number of available names
        # Skip names that are already in the domain_check_log.
        # Desired number of available names is specified by the "limit" variable in bash file "create_names.sh"
        name_str: str
        rejects = [None, "Reject"]
        dict_len = len(NameDomain_dict[name_type])
        for name_str in name_list:
            if name_str not in NameDomain_dict[name_type] and names_dict[name_type][name_str]["grade"] not in rejects:
                name_data = Graded_name(**names_dict[name_type][name_str])
                avail_domain_list = set()
                not_avail_domain_list = set()
                for tld in tld_list:
                    domain_log_use = ""
                    domain_str = name_str.lower() + tld
                    print(f"Checking {domain_str}...", end = "\r")

                    # Skip name if name is in domain_check_log
                    if not domain_str in checked_domains:
                        # Access whois API and add result to domain log
                        domain_obj: Domain = get_whois(domain_str)
                        domain_log_base.put(domain_obj.to_dict(), domain_obj.domain)
                    else:
                        try:
                            domain_obj: Domain = Domain.from_dict(domain_log_base.get(domain_str))
                            domain_log_use = " (Domain already checked!)"
                        except AttributeError:
                            domain_obj: Domain = get_whois(domain_str)
                            domain_log_base.put(domain_obj.to_dict(), domain_obj.domain)

                    sys.stdout.write("\033[K")

                    # If domain is available: add domain obj to avail_domain_list
                    if domain_obj.availability == DomainStates.AVAIL:
                        avail_domain_list.add(domain_obj)
                        condition = "available"
                    # If domain is not available: add domain obj to not_avail_domain_list
                    elif domain_obj.availability == DomainStates.NOT_AVAIL:
                        not_avail_domain_list.add(domain_obj)
                        condition = "not available"

                    if condition == "available":
                        available += 1
                        all_available += 1
                    counter += 1

                    print(f"'{domain_str}' {condition}{domain_log_use}")
                    print(f"Names processed: {counter}")
                    print(f"Names available: {available} + {dict_len}\n")
                    if available >= limit:
                        break

                NameDomain_obj = create_NameDomain_obj(name_data, list(avail_domain_list), list(not_avail_domain_list))
                NameDomain_dict[name_type][name_str] = NameDomain_obj
                del names_dict[name_type][name_str]
                if available >= limit:
                    break

        if available == 0:
            print(f"No available domains collected for {name_type}s... Moving on to next name type...")

    if all_available == 0:
        print(f"No available domains collected! Add more keyword to generate more names.")
        sys.exit()

    with open(json_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(NameDomain_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))
    with open(remaining_names_fp, "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    statuses = ["avail", "not_avail"]
    excel_domains = {}
    for name_type in name_types:
        excel_domains[name_type] = {}
        for status in statuses:
            excel_domains[name_type][status] = []

    for name_type, name_list in NameDomain_dict.items():
        data:NameDomain
        for name_in_title, data in name_list.items():
            for domain in data.avail_domains:
                excel_domains = create_excel_domain(name_type, "avail", data, domain, excel_domains)
            for domain in data.not_avail_domains:
                excel_domains = create_excel_domain(name_type, "not_avail", data, domain, excel_domains)

    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')
    workbook  = writer.book
    for status in statuses:
        for name_type in name_types:    
            domain_list = excel_domains[name_type][status]
            if len(domain_list) != 0:
                df = pd.DataFrame.from_dict(domain_list, orient="columns")
            else:
                df = pd.DataFrame.from_dict([{}], orient="columns")
            sheet_name = f"{status} {name_type} ({len(domain_list)})"
            df.to_excel(writer, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(1, 15, 20)
    writer.save()

if __name__ == "__main__":
    check_domains(sys.argv[1], sys.argv[2])
    sync_logs()