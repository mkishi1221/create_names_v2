#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from importlib.machinery import SourceFileLoader
from classes.domain_class import Domain
from datetime import datetime, timedelta
from time import sleep
import re
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import random

pois = SourceFileLoader("pois", "name_generator/modules/Pois/pois/__init__.py").load_module()

# Search domain database by calling the whois database in python
class DomainStates:
    AVAIL = "available"
    NOT_AVAIL = "not available"
    UNKNOWN = "connection error"

ua = UserAgent()
proxies = []

def random_proxy():
  return random.randint(0, len(proxies) - 1)

proxies_req = Request('https://www.sslproxies.org/')
proxies_req.add_header('User-Agent', ua.random)
proxies_doc = urlopen(proxies_req).read().decode('utf8')

soup = BeautifulSoup(proxies_doc, 'html.parser')
proxies_table = soup.find("table", { "class": "table table-striped table-bordered" })

# Save proxies in the array
for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
        'ip':   row.find_all('td')[0].string,
        'port': row.find_all('td')[1].string
    })

def get_whois(domain_str) -> Domain:

    # Call whois API to get domain information
    last_checked_int = None
    check_expiration = None
    status = None
    str_error = None

    sleep_time = 1
    num_retries = 5

    proxy = proxies[random_proxy()]
    proxy_info = {'proxy_type':'http','addr': proxy["ip"], 'port': proxy["port"]}
    p = pois.Pois(timeout=10, proxy_info=proxy_info)

    for x in range(0, num_retries):
        try:
            d = p.fetch(domain=domain_str)

            if d["registrar_result"] == None:
                check_expiration = int((datetime.now() + timedelta(days=1)).timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.AVAIL
            else:
                exp_date = re.findall(r"Registry Expiry Date: (.*T.*Z)", d["registry_result"])[0].replace("Z", "")
                check_expiration = int(datetime.fromisoformat(exp_date).timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.NOT_AVAIL

        except (pois.SocketError):
            check_expiration = int((datetime.now() + timedelta(days=1)).timestamp())
            last_checked_int = int(datetime.now().timestamp())
            status = DomainStates.AVAIL
        except (AttributeError) as e:
            str_error = str(e)
        if str_error:
            sleep(sleep_time)  # wait before trying to fetch the data again
        else:
            break
    
    if status is None:
        print("Connection unstable: check your internet connection and try again.")
        quit()

    data = Domain(domain=domain_str, availability=status, last_checked=last_checked_int, data_valid_till=check_expiration)

    return data

# For testing purposes:
# domains = ["brandbrand.co", "messaguides.co", "strategicreativity.co", ]
# for d in domains:
#     flags = 0
#     flags = flags | whois.NICClient.WHOIS_QUICK
#     name="strategicreativity.co"
#     w = whois.whois(name, flags=flags)
#     print(w)
