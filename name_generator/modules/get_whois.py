#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import whois
from classes.domain_class import Domain
from datetime import datetime, timedelta
from time import sleep

# Search domain database by calling the whois database in python
class DomainStates:
    AVAIL = "available"
    NOT_AVAIL = "not available"
    UNKNOWN = "connection error"

def get_whois(name) -> Domain:

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
            w = whois.whois(name, flags=flags)
            check_expiration = int(w.expiration_date.timestamp())
            last_checked_int = int(datetime.now().timestamp())
            status = DomainStates.NOT_AVAIL
        except (whois.parser.PywhoisError):
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

    data = Domain(domain=name, availability=status, last_checked=last_checked_int, data_valid_till=check_expiration)

    return data

# For testing purposes:
# print(get_whois("google.com"))
