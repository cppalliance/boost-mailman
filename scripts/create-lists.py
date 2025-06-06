#!/usr/bin/env python

# activate the venv first
# . /opt/mailman3/bin/activate
#
# Check the rest password in /etc/mailman3/mailman.cfg
# export REST_PASSWORD=

import requests
from mailman.testing.documentation import dump_json
import os

hostname = "lists.boost.org"
# check "domain" also.

port_number = "8001"
rest_user = "restadmin"
rest_password = os.environ["REST_PASSWORD"]

if not rest_password:
    print("please set rest_password. Exiting.")
    exit(1)

# DOMAINS

domain = "lists.boost.org"
url = f"http://{hostname}:{port_number}/3.1/domains"
dump_json(
    url,
    {
        "mail_host": domain,
    },
    username=rest_user,
    password=rest_password,
)

print("Next, view the result")

url = f"http://{hostname}:{port_number}/3.1/domains/{domain}"
dump_json(url, username=rest_user, password=rest_password)

# LISTS

print("Now for lists\n")

lists = [
    f"boost@{domain}",
    f"boost-announce@{domain}",
    f"boost-users@{domain}",
    f"test@{domain}",
]
url = f"http://{hostname}:{port_number}/3.1/lists"

for list in lists:
    dump_json(
        url,
        {
            "fqdn_listname": list,
        },
        username=rest_user,
        password=rest_password,
    )

print("Next, view the results")

for list in lists:
    url = f"http://{hostname}:{port_number}/3.1/lists/{list}"
    dump_json(url, username=rest_user, password=rest_password)
