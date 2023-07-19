#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from importlib.machinery import SourceFileLoader
from classes.domain_class import Domain
from datetime import datetime, timedelta
from time import sleep
import re
import sys
import logging

if "pytest" in sys.modules:
    pois_location = "modules/Pois/pois/__init__.py"
else:
    pois_location = "name_generator/modules/Pois/pois/__init__.py"

pois = SourceFileLoader("pois", pois_location).load_module()

# Search domain database by calling the whois database in python
class DomainStates:
    AVAIL = "available"
    NOT_AVAIL = "not available"
    UNKNOWN = "connection error"

def get_whois(domain_str) -> Domain:

    # Call whois API to get domain information
    last_checked_int = None
    check_expiration = None
    status = None
    str_error = None

    sleep_time = 1
    num_retries = 5

    proxy_info = {"proxy_type": "socks5", "addr": "p.webshare.io", "port": 80, "username": "ihgosdbs-rotate", "password": "a6au825lb0n3"}
    p = pois.Pois(timeout=10, proxy_info=proxy_info)

    for x in range(0, num_retries):
        try:
            d = p.fetch(domain=domain_str)

            raw_date = re.findall(r"Registry Expiry Date: (.*T.*Z)", d["registry_result"])
            try:
                exp_date = raw_date[0].replace("Z", "")
            except:
                exp_date = (datetime.now() + timedelta(days=1)).isoformat()

            if d["registrar_result"] == None or datetime.fromisoformat(exp_date) < datetime.now():
                check_expiration = int((datetime.now() + timedelta(days=1)).timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.AVAIL
            else:
                check_expiration = int(datetime.fromisoformat(exp_date).timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.NOT_AVAIL

        except (pois.SocketError) as e:
            logging.warn(e)
            check_expiration = int((datetime.now() + timedelta(days=1)).timestamp())
            last_checked_int = int(datetime.now().timestamp())
            status = DomainStates.NOT_AVAIL
        except (AttributeError) as e:
            str_error = str(e)
        if str_error:
            sleep(sleep_time)  # wait before trying to fetch the data again
        else:
            break
    
    if status is None:
        logging.error("Connection unstable: check your internet connection and try again.")
        quit()

    data = Domain(domain=domain_str, availability=status, last_checked=last_checked_int, data_valid_till=check_expiration)

    return data

# For testing purposes:
# google.com should be NOT_AVAIL
# masayukikishi1221.com should be AVAIL
domains = ["google.com", "masayukikishi1221.com"]
for d in domains:
    w = get_whois(d)
    print(w)
