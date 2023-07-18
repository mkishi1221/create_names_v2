# import whois

# def seeAllWHOISdata():
#     w = whois.whois('reddit.com')
#     print(w)

# seeAllWHOISdata()


# alphabet = "abcdefghijklmnopqrstuvwxyz"

# text = "asdhbs"

# print(text[-2:])
# print(all(letter in alphabet for letter in text))


# For testing purposes:
# # google.com should be NOT_AVAIL
# # masayukikishi1221.com should be AVAIL
from modules.get_whois import get_whois
domains = ["google.com", "masayukikishi1221.com"]
for d in domains:
    w = get_whois(d)
    print(w)
