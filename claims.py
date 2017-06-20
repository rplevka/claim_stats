from __future__ import division
import json
import requests
import yaml

requests.packages.urllib3.disable_warnings()
config = {}
# load config
with open("config.yaml", "r") as file:
    try:
        config = yaml.load(file)
    except yaml.YAMLERROR as exc:
        print(exc)

#PARAMS = {u'tree': u'suites[cases[className,name,status,testActions[reason]]]{0}'}
PARAMS = {u'tree': u'suites[cases[className,name,status,errorDetails,testActions[reason]]]{0}'}
ep = [u'ui', u'api', u'cli']

def fetch_test_report(url, job, build):
    bld_req = requests.get(
        u'{0}/job/{1}/{2}/testReport/api/json'.format(url, job, build),
        auth=requests.auth.HTTPBasicAuth(
            config['usr'],
            config['pwd']
        ),
        params=PARAMS,
        verify=False
    )

    if bld_req.status_code == 200:
        return(json.loads(bld_req.text)['suites'][0]['cases'])


def fetch_all_reports(job=None, build=None):
    if job is None:
        job = config['job']
    if build is None:
        build = config['bld']
    results = {}
    for i in range(1, 5):
        results['T{}'.format(i)] = {}
        for j in range(6, 8):
            job1 = job.format(i, j)
            tr = fetch_test_report(config['url'], job1, build)
            fails = parse_fails(tr)
            results['T{}'.format(i)]['el{}'.format(j)] = fails
    return(results)


def parse_fails(bld):
    return([i for i in bld if (i['status'] == "FAILED" or i['status'] == "ERROR" or i['status'] == "REGRESSION")])

# fetch_test_report(config['url'], config['job'], config['bld'])
# fetch the failed tests with claim reasons
# bld = fetch_test_report(config['url'], config['job'], config['build'])


def parse_reasons(fails):
    reasons = {}
    for f in fails:
        if reasons.get(str(f['testActions'][0]['reason'])):
            reasons[str(f['testActions'][0]['reason'])] += 1
        else:
            reasons[str(f['testActions'][0]['reason'])] = 1
    return(reasons)


def get_endpoints_ratio(tests, ep):
    endpoints = {i: 0 for i in ep}
    for t in tests:
        for e in endpoints.keys():
            if u'tests.foreman.{}'.format(e) in t['className']:
                endpoints[e] += 1
    return endpoints


def get_endpoints_failure_ratio(total, fails):
    f = get_endpoints_ratio(fails, ep)
    t = get_endpoints_ratio(total, ep)
    return {i: (f[i] / t[i]) * 100 for i in ep}


def claim(test, reason, sticky=False, url=None, job=None, build=None):
    # json={"assignee": "", "reason": "bot", "sticky": false}
    className = test['className'].split('.')[-1]
    testPath = '.'.join(test['className'].split('.')[:-1])
    if url is None:
        url = config['url']
    if job is None:
        job = config['job']
    if build is None:
        build = config['bld']
    claim_req = requests.post(
        u'{0}/job/{1}/{2}/testReport/junit/{3}/{4}/{5}/claim/claim'.format(url, job, build, testPath, className, test['name']),
        auth=requests.auth.HTTPBasicAuth(
            config['usr'],
            config['pwd']
        ),
        data={u'json': u'{{"assignee": "", "reason": "{0}", "sticky": {1}}}'.format(reason, sticky)},
        allow_redirects=False,
        verify=False
    )
    return(claim_req)
