#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.domain_class import Domain
from classes.domain_class import NameDomain
from classes.name_class import Graded_name
from modules.get_whois import get_whois, DomainStates
import sys
import time
import orjson as json
import pandas as pd
from datetime import datetime
from typing import List
import os
import copy

def create_NameDomain_obj(name_data: Graded_name, avail_domain_list: List[Domain], not_avail_domain_list: List[Domain]):
    return NameDomain (
        name_in_title=name_data.name_in_title,
        name_in_lower=name_data.name_in_lower,
        name_type=name_data.name_type,
        length=name_data.length,
        phonetic_grade=name_data.phonetic_grade,
        keywords=name_data.keywords,
        keyword_combinations=name_data.keyword_combinations,
        pos_combinations=name_data.pos_combinations,
        modifier_combinations=name_data.modifier_combinations,
        etymologies=name_data.etymologies,
        avail_domains=avail_domain_list,
        not_avail_domains=not_avail_domain_list,
        grade=name_data.grade,
    )

# Checks domain availability using whois
def check_domains(project_id: str, limit: int):

    project_path = f"projects/{project_id}"

    # input file filepaths and filenames:
    sl_namelist_fp: str = f"{project_path}/tmp/name_generator/{project_id}_names_shortlist.json"

    # dict resource paths and filenames:
    domain_log_fp = "name_generator/dict/domain_log.json"

    # tmp file filepaths and filenames:
    json_output_fp: str = f"{project_path}/tmp/domain_checker/{project_id}_domains.json"
    json_ndl_output_fp = f"{project_path}/tmp/domain_checker/{project_id}_namedomain_list_domains.json"
    remaining_names_fp = f"{project_path}/tmp/domain_checker/{project_id}_remaining_name_shortlist.json"

    # output filepaths and filenames:
    excel_output_fp = f"{project_path}/results/{project_id}_domains.xlsx"

    limit = int(limit)    
    domain_log = {}

    if os.path.exists(domain_log_fp):
        print("Domain log found - adding items to domain log...")
        with open(domain_log_fp) as domain_log_file:
            domain_log_raw = json.loads(domain_log_file.read())
        for domain, data in domain_log_raw.items():
            if data["data_valid_till"] > datetime.now().timestamp():
                domain_log[domain] = Domain(
                    domain= data["domain"],
                    availability= data["availability"],
                    last_checked= data["last_checked"],
                    data_valid_till= data["data_valid_till"],
                    shortlist= data["shortlist"]
                )
            else:
                valid_till = data["data_valid_till"]
                print(f"{domain} check validity expired! Expired in {time.strftime('%d-%b-%Y (%H:%M:%S)').format(valid_till)} Removing from list...")
    else:
        print("Domain log not found - creating new domain log...")

    # Open file with generated names
    if os.path.exists(remaining_names_fp):
        with open(remaining_names_fp, "rb") as namelist_file:
            names_dict = json.loads(namelist_file.read())
        remaining = sum([len(names_dict[name_type].keys()) for name_type in names_dict.keys()])
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"No new names detected. {remaining} names remaining...")

    else:
        with open(sl_namelist_fp, "rb") as namelist_file:
            names_dict = json.loads(namelist_file.read())
        remaining = sum([len(names_dict[name_type].keys()) for name_type in names_dict.keys()])
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"New names detected. Using {remaining} new names...")

    if os.path.exists(json_output_fp):
        print("Previous domain check detected. Continuing domain check...")
        with open(json_output_fp, "rb") as NameDomain_file:
            NameDomain_dict_raw: dict = json.loads(NameDomain_file.read())
        NameDomain_dict = {}
        NameDomain_dict["cut_name"] = {}
        NameDomain_dict["pref_suff_name"] = {}
        NameDomain_dict["text_comp_name"] = {}
        NameDomain_dict["no_cut_name"] = {}
        name_list: dict
        for name_type, name_list in NameDomain_dict_raw.items():
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

    else:
        NameDomain_dict = {}
        NameDomain_dict["cut_name"] = {}
        NameDomain_dict["pref_suff_name"] = {}
        NameDomain_dict["text_comp_name"] = {}
        NameDomain_dict["no_cut_name"] = {}

    tld_list = [".com"] #TODO: Change to file source

    json_ndl_output_fp = json_output_fp.replace("tmp/domain_checker/", "tmp/domain_checker/namedomain_list_")
    with open(json_ndl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    counter = 0
    for name_type in names_dict.keys():

        print(f"Checking domains for {name_type}s...")

        name_list = list(names_dict[name_type].keys())
        # random.shuffle(name_list)
        available = 0
        domain_log_use = ""

        # Check names from top of the shuffled name list until it reaches the desired number of available names
        # Skip names that are already in the domain_check_log.
        # Desired number of available names is specified by the "limit" variable in bash file "create_names.sh"
        name_str: str
        dict_len = len(NameDomain_dict[name_type])
        for name_str in name_list:
            if name_str not in NameDomain_dict[name_type]:
                name_data = Graded_name(**names_dict[name_type][name_str])
                avail_domain_list = set()
                not_avail_domain_list = set()

                for tld in tld_list:
                    domain_str = name_str.lower() + tld
                    print(f"Checking {domain_str}...", end = "\r")

                    # Skip name if name is in domain_check_log
                    if domain_str not in domain_log.keys():
                        # Access whois API and add result to domain log
                        domain_obj: Domain = get_whois(domain_str)
                        domain_log[domain_str] = domain_obj
                    else:
                        domain_obj: Domain = domain_log[domain_str]
                        domain_log_use = " (Domain already checked!)"

                    sys.stdout.write("\033[K")

                    # If domain is available: add domain obj to avail_domain_list
                    if domain_obj.availability == DomainStates.AVAIL:
                        avail_domain_list.add(domain_obj)
                        condition = "available"
                    # If domain is not available: add domain obj to not_avail_domain_list
                    elif domain_obj.availability == DomainStates.NOT_AVAIL:
                        not_avail_domain_list.add(domain_obj)
                        condition = "not available"

                    print(f"'{domain_str}' {condition}{domain_log_use}")

                del names_dict[name_type][name_str]
                NameDomain_obj = create_NameDomain_obj(name_data, list(avail_domain_list), list(not_avail_domain_list))
                NameDomain_dict[name_type][name_str] = NameDomain_obj

                if len(avail_domain_list) > 0:
                    available += 1

                print(f"Names processed: {counter}\nNames available: {available} + {dict_len}\n")

                counter += 1
                if available == limit:
                    break

        if available == 0:
            print("No available domains collected. Add more source data and generate new names.")
            sys.exit()

    with open(json_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(NameDomain_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))
    with open(remaining_names_fp, "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))
    with open(domain_log_fp, "wb+") as out_file:
        out_file.write(json.dumps(domain_log, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    # Export to excel file
    cut_name_avail = []
    cut_name_not_avail = []
    pref_suff_name_avail = []
    pref_suff_name_not_avail = []
    text_comp_name_avail = []
    text_comp_name_not_avail = []
    no_cut_name_avail = []
    no_cut_name_not_avail = []

    for name_type, name_list in NameDomain_dict.items():
        data:NameDomain
        for name_in_title, data in name_list.items():
            domain:Domain
            for domain in data.avail_domains:
                excel_domain = {
                    "name_in_lower": data.name_in_lower,
                    "name_in_title": data.name_in_title,
                    "domain": domain.domain,
                    "length": data.length,
                    "phonetic_grade": data.phonetic_grade,
                    "keywords": data.keywords,
                    "keyword_combinations": data.keyword_combinations,
                    "pos_combinations": data.pos_combinations,
                    "modifier_combinations": data.modifier_combinations,
                    "etymologies": data.etymologies,
                    "grade": data.grade,
                    "last_checked": time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain.last_checked),
                    "data_valid_till": time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain.data_valid_till),
                    "availability": domain.availability,
                    "shortlist": domain.shortlist,
                }
                if name_type == "cut_name":
                    cut_name_avail.append(excel_domain)
                elif name_type == "pref_suff_name":
                    pref_suff_name_avail.append(excel_domain)
                elif name_type == "text_comp_name":
                    text_comp_name_avail.append(excel_domain)
                elif name_type == "no_cut_name":
                    no_cut_name_avail.append(excel_domain)

            domain:Domain
            for domain in data.not_avail_domains:
                excel_domain = {
                    "name_in_lower": data.name_in_lower,
                    "name_in_title": data.name_in_title,
                    "domain": domain.domain,
                    "length": data.length,
                    "phonetic_grade": data.phonetic_grade,
                    "keywords": data.keywords,
                    "keyword_combinations": data.keyword_combinations,
                    "pos_combinations": data.pos_combinations,
                    "pos_combinations": data.pos_combinations,
                    "modifier_combinations": data.modifier_combinations,
                    "etymologies": data.etymologies,
                    "grade": data.grade,
                    "domain": domain.domain,
                    "last_checked": time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain.last_checked),
                    "data_valid_till": time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain.data_valid_till),
                    "availability": domain.availability,
                    "shortlist": domain.shortlist,
                }
                if name_type == "cut_name":
                    cut_name_not_avail.append(excel_domain)
                elif name_type == "pref_suff_name":
                    pref_suff_name_not_avail.append(excel_domain)
                elif name_type == "text_comp_name":
                    text_comp_name_not_avail.append(excel_domain)
                elif name_type == "no_cut_name":
                    no_cut_name_not_avail.append(excel_domain)

    cut_name_avail_len = len(cut_name_avail)
    cut_name_not_avail_len = len(cut_name_not_avail)
    pref_suff_name_avail_len = len(pref_suff_name_avail)
    pref_suff_name_not_avail_len = len(pref_suff_name_not_avail)
    text_comp_name_avail_len = len(text_comp_name_avail)
    text_comp_name_not_avail_len = len(text_comp_name_not_avail)
    no_cut_name_avail_len = len(no_cut_name_avail)
    no_cut_name_not_avail_len = len(no_cut_name_not_avail)

    df1 = pd.DataFrame.from_dict(cut_name_avail, orient="columns")
    df2 = pd.DataFrame.from_dict(pref_suff_name_avail, orient="columns")
    df3 = pd.DataFrame.from_dict(text_comp_name_avail, orient="columns")
    df4 = pd.DataFrame.from_dict(no_cut_name_avail, orient="columns")
    df5 = pd.DataFrame.from_dict(cut_name_not_avail, orient="columns")
    df6 = pd.DataFrame.from_dict(pref_suff_name_not_avail, orient="columns")
    df7 = pd.DataFrame.from_dict(text_comp_name_not_avail, orient="columns")
    df8 = pd.DataFrame.from_dict(no_cut_name_not_avail, orient="columns")

    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')

    # Set sheet names:
    sheet_names = [
        f'avail cut names ({cut_name_avail_len})',
        f'avail pref suff names ({pref_suff_name_avail_len})',
        f'avail text comp names ({text_comp_name_avail_len})',
        f'avail no cut names ({no_cut_name_avail_len})',
        f'unavail cut names ({cut_name_not_avail_len})',
        f'unavail pref suff names ({pref_suff_name_not_avail_len})',
        f'unavail text comp names ({text_comp_name_not_avail_len})',
        f'unavail no cut names ({no_cut_name_not_avail_len})'
    ]

    df1.to_excel(writer, sheet_name=sheet_names[0])
    df2.to_excel(writer, sheet_name=sheet_names[1])
    df3.to_excel(writer, sheet_name=sheet_names[2])
    df4.to_excel(writer, sheet_name=sheet_names[3])
    df5.to_excel(writer, sheet_name=sheet_names[4])
    df6.to_excel(writer, sheet_name=sheet_names[5])
    df7.to_excel(writer, sheet_name=sheet_names[6])
    df8.to_excel(writer, sheet_name=sheet_names[7])
    workbook  = writer.book
    for sheet_name in sheet_names:
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column(1, 15, 20)
    writer.save()

if __name__ == "__main__":
    check_domains(sys.argv[1], sys.argv[2])


