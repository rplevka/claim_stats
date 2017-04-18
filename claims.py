#!/usr/bin/python
import json
import requests
import yaml

config = {}
# load config
with open("config.yaml", "r") as file:
    try:
        config = yaml.load(file)
    except yaml.YAMLERROR as exc:
        print(exc)

PARAMS = {u'tree': u'suites[cases[className,name,status,testActions[reason]]]{0}'}

# fetch the failed tests with claim reasons
bld_req = requests.get(
    u'{0}/job/{1}/{2}/testReport/api/json'.format(
        config['url'],
        config['job'],
        config['bld']
    ),
    auth=requests.auth.HTTPBasicAuth(
        config['usr'],
        config['pwd']
    ),
    params=PARAMS,
    verify=False
)

if bld_req.status_code == 200:
    bld = json.loads(bld_req.text)['suites'][0]['cases']

    fails = [i for i in bld if (i['status'] == "FAILED" or i['status'] == "ERROR" or i['status'] == "REGRESSION")]
    reasons = {}
    for f in fails:
        if reasons.get(str(f['testActions'][0]['reason'])):
            reasons[str(f['testActions'][0]['reason'])] += 1
        else:
            reasons[str(f['testActions'][0]['reason'])] = 1
    print(json.dumps(reasons))
