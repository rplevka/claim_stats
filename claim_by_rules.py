import claims
import sys

try:
    target_url = sys.argv[1]
except IndexError:
    raise ValueError('The targe url is supposed to be passed as an argument '
                     'to this script')

rules = claims.load_rules()
r = claims.fetch_test_report(build_url=target_url)
f = claims.filter_fails(r)
# let's only take the unclaimed tests
u = claims.filter_not_claimed(f)

claims.claim_by_rules(u, rules)
