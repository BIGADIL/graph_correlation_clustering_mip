import gzip
import json
import os
import time
import xmlrpc.client as xmlrpclib

from mip_impl.min_disagree_models import *

NAME = "k-3-n-25-p-0.330000"
path_to_data = os.path.join("data", NAME + ".json")
neos = xmlrpclib.ServerProxy("https://neos-server.org:3333")

SUFFIX = ".mps.mps.gz"


def send_request_for_model(lines):
    request = "<document>\n"
    request += "<category>milp</category>\n"
    request += "<solver>Cplex</solver>\n"
    request += "<inputMethod>MPS</inputMethod>\n"
    request += "<priority><![CDATA[long]]></priority>\n"
    request += "<email><![CDATA[svegmolod@gmail.com]]></email>\n"
    request += "<MPS><![CDATA[\n"
    for line in lines:
        request += line
    request += "]]></MPS>\n"
    request += "<param><![CDATA[]]></param>\n"
    request += "<BAS><![CDATA[]]></BAS>\n"
    request += "<MST><![CDATA[]]></MST>\n"
    request += "<SOL><![CDATA[]]></SOL>\n"
    request += "<comments><![CDATA[]]></comments>\n"
    request += "</document>"
    while True:
        x = neos.submitJob(request)
        print(i, ":", x)
        if "Error:" not in x[1]:
            break
        time.sleep(5)


if __name__ == "__main__":
    with open(path_to_data, 'r') as f_json:
        data = json.load(f_json)
    for i in range(len(data)):
        d = data[i]
        model = MDAMIPTriangleModelLeqK(graph=d["graph"], k=3)
        model.write_as_mps(str(i))
        mps = os.path.join(str(i) + SUFFIX)
        mps = gzip.open(mps, 'rb')
        lines = mps.read().decode("UTF-8").split("\r\n")
        mps.close()
        os.remove(str(i) + SUFFIX)
        send_request_for_model(lines)
