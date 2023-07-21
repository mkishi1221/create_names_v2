#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.domain_class import Domain
from datetime import datetime, timedelta
from time import sleep
import logging
import whois


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

    for x in range(0, num_retries):
        try:
            flags = 0
            flags = flags | whois.NICClient.WHOIS_QUICK
            d = whois.whois(domain_str, flags=flags)

            if d.domain_name is None:
                check_expiration = int((datetime.now() + timedelta(days=1)).timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.AVAIL
            else:
                check_expiration = int(d.expiration_date.timestamp())
                last_checked_int = int(datetime.now().timestamp())
                status = DomainStates.NOT_AVAIL

        except (whois.parser.PywhoisError) as e:
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
""" domains = ["google.com", "masayukikishi1221.com"]
for d in domains:
    w = get_whois(d)
    print(w) """
