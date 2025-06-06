#!/usr/bin/env python

# activate the venv first
# . /opt/mailman3/bin/activate
#
# Check the rest password in /etc/mailman3/mailman.cfg
# export REST_PASSWORD=

import requests
from mailman.testing.documentation import dump_json
import os
import subprocess

hostname = subprocess.check_output("hostname -f", shell=True).decode().strip()
print(f"hostname is {hostname}")

port_number = "8001"
rest_user = "restadmin"
rest_password = os.environ["REST_PASSWORD"]

if not rest_password:
    print("please set rest_password. Exiting.")
    exit(1)

urls = {}
urls["boost"] = f"http://{hostname}:{port_number}/3.1/lists/boost@{hostname}/config"
urls["Boost-announce"] = (
    f"http://{hostname}:{port_number}/3.1/lists/boost-announce@{hostname}/config"
)
urls["Boost-users"] = (
    f"http://{hostname}:{port_number}/3.1/lists/boost-users@{hostname}/config"
)
settings = {}
settings["boost"] = dict(
    default_nonmember_action="reject",
    convert_html_to_plaintext="True",
    filter_content="True",
    dmarc_mitigate_action="munge_from",
    reply_goes_to_list="point_to_list",
    subject_prefix="[boost] ",
)
settings["Boost-announce"] = dict(
    default_nonmember_action="reject",
    convert_html_to_plaintext="True",
    filter_content="True",
    dmarc_mitigate_action="munge_from",
    reply_goes_to_list="point_to_list",
    subject_prefix="[Boost-announce] ",
)
settings["Boost-users"] = dict(
    default_nonmember_action="reject",
    convert_html_to_plaintext="True",
    filter_content="True",
    dmarc_mitigate_action="munge_from",
    reply_goes_to_list="point_to_list",
    subject_prefix="[Boost-users] ",
)

for listname, request_url in urls.items():
    print(f"listname is {listname} and request_url is {request_url}")
    print("running dump_json")
    dump_json(request_url, username=rest_user, password=rest_password)
