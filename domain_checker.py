#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.domain_class import Domain
from classes.domain_class import NameDomain
from modules.get_whois import get_whois, DomainStates
import sys
import time
import random
import orjson as json
import pandas as pd
from datetime import datetime
from typing import List, Dict
import os
import copy

def create_NameDomain_obj(name_data: Dict, avail_domain_list: List[Domain], not_avail_domain_list: List[Domain]):
    return NameDomain (
        name_in_lower=name_data["name_in_lower"],
        length=name_data["length"],
        length_score=name_data["length_score"],
        total_score=name_data["total_score"],
        avail_domains=avail_domain_list,
        not_avail_domains=not_avail_domain_list,
        etymologies=name_data["etymologies"]
    )

# Checks domain availability using whois
def check_domains(sl_namelist_fp: str, limit: int, json_output_fp: str):

    limit = int(limit)
    domain_log_fp = "tmp/domain_log.json"
    remaining_names_fp = "tmp/remaining_shortlist.json"
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
        remaining = len(names_dict.keys())
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"No new names detected. {remaining} names remaining...")

    else:
        with open(sl_namelist_fp, "rb") as namelist_file:
            names_dict = json.loads(namelist_file.read())
        remaining = len(names_dict.keys())
        if remaining == 0:
            print("No names left - run name generator again!")
            exit()
        else:
            print(f"New names detected. Using {remaining} new names...")

    if os.path.exists(json_output_fp):
        print("Previous domain check detected. Continuing domain check...")
        with open(json_output_fp, "rb") as NameDomain_file:
            NameDomain_dict_raw = json.loads(NameDomain_file.read())
        NameDomain_dict = {}
        for name, data in NameDomain_dict_raw.items():
            avail_domains_list = []
            for domain_obj in data["avail_domains"]:
                avail_domains_list.append(Domain(**domain_obj))
            not_avail_domains_list = []
            for domain_obj in data["not_avail_domains"]:
                not_avail_domains_list.append(Domain(**domain_obj))
            data = copy.deepcopy(data)
            data["avail_domains"] = avail_domains_list
            data["not_avail_domains"] = not_avail_domains_list
            NameDomain_dict[name] = NameDomain(**data)

    else:
        NameDomain_dict = {}

    tld_list = [".com"] #TODO: Change to file source

    # Shuffle pre-generated names from the name generator and sort by name score.
    # This is so that the names don't get picked in alphabetical order but names with higher scores are prioritized.
    name_list = list(names_dict.keys())
    random.shuffle(name_list)

    counter = 0
    available = 0
    error_count = 0

    # Check names from top of the shuffled name list until it reaches the desired number of available names
    # Skip names that are already in the domain_check_log.
    # Desired number of available names is specified by the "limit" variable in bash file "create_names.sh"
    for name_str in name_list:

        if error_count == 5:
            print("Connection unstable: check your internet connection.")
            break
        elif available == limit:
            break

        name_data = names_dict[name_str]

        avail_domain_list = []
        not_avail_domain_list = []
        skip = None

        for tld in tld_list:

            domain_str = name_str + tld

            print(f"Checking {domain_str}...")

            # Skip name if name is in domain_check_log
            if domain_str in domain_log.keys():
                print(f"'{domain_str}' already checked")
                valid_till = domain_log[domain_str].data_valid_till
                print(f"Expiration date: {time.strftime('%d-%b-%Y (%H:%M:%S)').format(valid_till)}")
                print(
                        f"Date checked: {time.strftime('%d-%b-%Y (%H:%M:%S)').format(domain_obj.last_checked)}"
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

                    # Stop the script for 1 second to make sure API is not overcalled.
                    time.sleep(1)
                # If connection error
                elif domain_obj.availability == DomainStates.UNKNOWN:
                    error_count += 1

        del names_dict[name_str]
        NameDomain_obj = create_NameDomain_obj(name_data, avail_domain_list, not_avail_domain_list)
        NameDomain_dict[name_str] = NameDomain_obj

        if len(avail_domain_list) > 0:
            available += 1

        if skip == None:
            counter += 1
        print(f"Names processed: {counter}")
        print(f"Names available: {available}", "\n")

    if available == 0:
        print(
            "No available domains collected. Check your internet connection or add more source data."
        )
        sys.exit()

    with open(json_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(NameDomain_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    with open("tmp/remaining_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(names_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    with open(domain_log_fp, "wb+") as out_file:
        out_file.write(json.dumps(domain_log, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))



    # Export to excel file
    xlsx_output_fp = json_output_fp.replace(".json", ".xlsx")

    available_domains_excel = []

    for name, data in NameDomain_dict.items():
        for domain in data.avail_domains:
            available_domains_excel.append(domain)
        for domain in data.not_avail_domains:
            available_domains_excel.append(domain)

    df1 = pd.DataFrame.from_dict(available_domains_excel, orient="columns")
    df1.to_excel(xlsx_output_fp)

if __name__ == "__main__":
    check_domains(sys.argv[1], sys.argv[2], sys.argv[3])


