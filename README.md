A set of scripts for easier parsing and batch processing of the Jenkins test reports.

Usage Examples:

Parse all tiers for the last completed builds of the job
```
In [1]: import claims

In [2]: claims.config
Out[2]: 
{'bld': 'lastCompletedBuild',
 'job': 'automation-6.2-tier{0}-rhel{1}',
 'pwd': 'nbusr123',
 'url': 'https://jenkins.server.com',
 'usr': 'uradnik1'}

In [5]: reports
Out[5]: 
['t1':
	[
		'el6': [
			{
			u'className': u'tests.foreman.cli.test_syncplan.SyncPlanTestCase',
			 u'errorDetails': None,
			 u'errorStackTrace': None,
			 u'name': u'test_negative_synchronize_custom_product_past_sync_date',
			 u'status': u'PASSED',
			 u'testActions': [],
			 'url': u'https://jenkins.server.com/job/automation-6.2-tier4-rhel7/lastCompletedBuild/testReport/junit/tests.foreman.cli.test_syncplan/SyncPlanTestCase/test_negative_synchronize_custom_product_past_sync_date'
			}
		],
		'el7': [
			{...}
		]
	],
't2': [...],
...
]
```

Get a flat list of all failed tests:
```
In [6]: failures = []

In [7]: for i in reports.keys():
   ...:     for j in reports[i].keys():
   ...:         failures += claims.parse_fails(reports[i][j])
   ...:         

In [8]: len(failures)
Out[8]: 324
In [9]: failures
Out[9]: 
[
	{u'className': u'tests.foreman.cli.test_syncplan.SyncPlanTestCase',
	 u'errorDetails': u'AssertionError: Repository contains invalid number of content entities',
	 u'errorStackTrace': u'self = <tests.foreman.cli.test_syncplan.SyncPlanTestCase ...',
	 u'name': u'test_positive_synchronize_custom_product_past_sync_date',
	 u'status': u'FAILED',
	 u'testActions': [{u'reason': None}],
	 'url': u'https://jenkins.server.com/job/automation-6.2-tier4-rhel6/lastCompletedBuild/testReport/junit/tests.foreman.cli.test_syncplan/SyncPlanTestCase/test_positive_synchronize_custom_product_past_sync_date'
	},
	{...},
	...
]
```

Claim unclaimed tests, containing 'foo' in the errorDetails with a reason: 'bar':
```
for f in [i for i in failures if u'foo' in i['errorDetails'] and not i['testActions'][0]['reason']]:
	claims.claim(f, 'bar')
```

Iterate over a list of failures and claim them based on the provided ruleset:

```
#load the ruleset (from kb.json)
In [10]: rules = claims.load_rules()

In [11]: rules
Out[11]: 
[{u'pattern': u'StaleElementReferenceException',
  u'reason': u'https://github.com/SatelliteQE/robottelo/issues/4162'},
 {u'pattern': u'HTTPError: 500 Server Error: Internal Server Error for url: https://jenkins.server.com/docker/api/v2/containers',
  u'reason': u'https://bugzilla.redhat.com/show_bug.cgi?id=1414821'},
 {u'pattern': u'Unable to log in to this Docker Registry - 404 Resource Not Found: 404 page not found',
  u'reason': u'docker_infra_error'},
 {u'pattern': u'VirtualMachineError: Failed to fetch virtual machine IP address information',
  u'reason': u'https://github.com/SatelliteQE/robottelo/issues/4578'},
 {u'pattern': u'Forbidden - server refused to process the request[^$]+Could not enable repository',
  u'reason': u'outdated_subscription'},
 {u'pattern': u'HTTPError: 403 Client Error: Forbidden for url[^$]+repository_sets[^$]+enable',
  u'reason': u'outdated_subscription'},
 {u'pattern': u'TaskTimedOutError[^$]+action[^$]+Manifest',
  u'reason': u'https://bugzilla.redhat.com/show_bug.cgi?id=1339696'},
 {u'pattern': u'SSHCommandTimeoutError:[^$]+hammer[^$+subscription]',
  u'reason': u'https://bugzilla.redhat.com/show_bug.cgi?id=1339696'}]

In [12]: claims.claim_by_rules(failures, rules)
```
