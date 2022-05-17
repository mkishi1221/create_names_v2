#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.domain_class import Domain
from classes.domain_class import NameDomain
from classes.name_class import Graded_name
from modules.get_whois import get_whois, DomainStates
import sys
import time
import random
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
def check_domains(sl_namelist_fp: str, limit: int, json_output_fp: str):

    limit = int(limit)
    domain_log_fp = "tmp/domain_checker/domain_log.json"
    remaining_names_fp = "tmp/domain_checker/remaining_shortlist.json"
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
        NameDomain_dict["text_comp_name"] = {}
        NameDomain_dict["no_cut_name"] = {}

    tld_list = [".com"] #TODO: Change to file source

    counter = 0
    for name_type in names_dict.keys():

        print(f"Checking domains for {name_type}s...")

        name_list = list(names_dict[name_type].keys())
        random.shuffle(name_list)
        available = 0
        error_count = 0

        # Check names from top of the shuffled name list until it reaches the desired number of available names
        # Skip names that are already in the domain_check_log.
        # Desired number of available names is specified by the "limit" variable in bash file "create_names.sh"
        name_str: str
        for name_str in name_list:

            if error_count == 5:
                print("Connection unstable: check your internet connection.")
                break
            elif available == limit:
                break

            name_data = Graded_name(**names_dict[name_type][name_str])
            avail_domain_list = []
            not_avail_domain_list = []
            skip = None

            for tld in tld_list:
                domain_str = name_str.lower() + tld
                print(f"Checking {domain_str}...", end = "\r")

                # Skip name if name is in domain_check_log
                if domain_str in domain_log.keys():
                    print(f"'{domain_str}' already checked")
                    valid_till = domain_log[domain_str].data_valid_till
                    print(f"Expiration date: {time.strftime('%d-%b-%Y (%H:%M:%S)').format(valid_till)}")
                    print(
                            f"Date checked: {time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain_log[domain_str].last_checked)}"
                        )
                    skip = "skipped"

                else:
                    # Access whois API and add result to domain log
                    domain_obj: Domain = get_whois(domain_str)
                    domain_log[domain_str] = domain_obj
                    # If domain is available: add domain obj to avail_domain_list
                    if domain_obj.availability == DomainStates.AVAIL:
                        avail_domain_list.append(domain_obj)
                        print(f"{domain_str} available")
                    # If domain is not available: add domain obj to not_avail_domain_list
                    elif domain_obj.availability == DomainStates.NOT_AVAIL:
                        not_avail_domain_list.append(domain_obj)
                        print(f"{domain_str} not available.")
                        print(
                            f"Expiration date: {time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain_obj.data_valid_till)}"
                        )
                    # If connection error
                    elif domain_obj.availability == DomainStates.UNKNOWN:
                        error_count += 1

                sys.stdout.write("\033[K")

            del names_dict[name_type][name_str]
            NameDomain_obj = create_NameDomain_obj(name_data, avail_domain_list, not_avail_domain_list)
            NameDomain_dict[name_type][name_str] = NameDomain_obj

            if len(avail_domain_list) > 0:
                available += 1

            if skip == None:
                counter += 1
            print(f"Names processed: {counter}\nNames available: {available}\n")


        if available == 0:
            print(
                "No available domains collected. Check your internet connection or add more source data."
            )
            sys.exit()

    with open(json_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(NameDomain_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    with open("tmp/domain_checker/remaining_name_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    with open(domain_log_fp, "wb+") as out_file:
        out_file.write(json.dumps(domain_log, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    # Export to excel file
    excel_output_fp = json_output_fp.replace(".json", ".xlsx").replace("tmp/domain_checker/", "results/")
    cut_name_avail = []
    cut_name_not_avail = []
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
                    "pos_combinations": data.pos_combinations,
                    "modifier_combinations": data.modifier_combinations,
                    "etymologies": data.etymologies,
                    "grade": data.grade,
                    "last_checked": domain.last_checked,
                    "data_valid_till": domain.data_valid_till,
                    "availability": domain.availability,
                    "shortlist": domain.shortlist,
                }
                if name_type == "cut_name":
                    cut_name_avail.append(excel_domain)
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
                    "last_checked": domain.last_checked,
                    "data_valid_till": domain.data_valid_till,
                    "availability": domain.availability,
                    "shortlist": domain.shortlist,
                }
                if name_type == "cut_name":
                    cut_name_not_avail.append(excel_domain)
                elif name_type == "text_comp_name":
                    text_comp_name_not_avail.append(excel_domain)
                elif name_type == "no_cut_name":
                    no_cut_name_not_avail.append(excel_domain)

    cut_name_avail = sorted(cut_name_avail, key=lambda d: (d['length'], d['grade'], d['domain']))
    cut_name_not_avail = sorted(cut_name_not_avail, key=lambda d: (d['length'], d['grade'], d['domain']))
    text_comp_name_avail = sorted(text_comp_name_avail, key=lambda d: (d['length'], d['grade'], d['domain']))
    text_comp_name_not_avail = sorted(text_comp_name_not_avail, key=lambda d: (d['length'], d['grade'], d['domain']))
    no_cut_name_avail = sorted(no_cut_name_avail, key=lambda d: (d['length'], d['grade'], d['domain']))
    no_cut_name_not_avail = sorted(no_cut_name_not_avail, key=lambda d: (d['length'], d['grade'], d['domain']))

    cut_name_avail_len = len(cut_name_avail)
    cut_name_not_avail_len = len(cut_name_not_avail)
    text_comp_name_avail_len = len(text_comp_name_avail)
    text_comp_name_not_avail_len = len(text_comp_name_not_avail)
    no_cut_name_avail_len = len(no_cut_name_avail)
    no_cut_name_not_avail_len = len(no_cut_name_not_avail)

    df1 = pd.DataFrame.from_dict(cut_name_avail, orient="columns")
    df2 = pd.DataFrame.from_dict(text_comp_name_avail, orient="columns")
    df3 = pd.DataFrame.from_dict(no_cut_name_avail, orient="columns")
    df4 = pd.DataFrame.from_dict(cut_name_not_avail, orient="columns")
    df5 = pd.DataFrame.from_dict(text_comp_name_not_avail, orient="columns")
    df6 = pd.DataFrame.from_dict(no_cut_name_not_avail, orient="columns")

    writer = pd.ExcelWriter(excel_output_fp)
    df1.to_excel(writer, sheet_name=f'avail cut names ({cut_name_avail_len})')
    df2.to_excel(writer, sheet_name=f'avail text comp names ({text_comp_name_avail_len})')
    df3.to_excel(writer, sheet_name=f'avail no cut names ({no_cut_name_avail_len})')
    df4.to_excel(writer, sheet_name=f'unavail cut names ({cut_name_not_avail_len})')
    df5.to_excel(writer, sheet_name=f'unavail text comp names ({text_comp_name_not_avail_len})')
    df6.to_excel(writer, sheet_name=f'unavail no cut names ({no_cut_name_not_avail_len})')
    writer.save()

if __name__ == "__main__":
    check_domains(sys.argv[1], sys.argv[2], sys.argv[3])


