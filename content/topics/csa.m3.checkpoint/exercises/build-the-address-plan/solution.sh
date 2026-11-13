# A reference, one layout among many: the checks hold rules, not answers.
# First the requirements, then the arithmetic (README rules 2, 4 and 5),
# then the plan, written whole. cat > FILE <<'EOF' writes the lines up to
# EOF into FILE.
cat /srv/plan/README.txt /srv/plan/sites.csv /srv/plan/policy.txt
#
# Each region: machines x 3 + the cloud's reserved addresses a subnet, up
# to a power of two; twice the subnets; up to a power of two again.
#   aws-us-east: 300 x 3 + 5 = 905 addresses a subnet, so a /22; 6 x 2 = 12 subnets x 1024 = 12288, so a /18
#   aws-us-west: 80 x 3 + 5 = 245 addresses a subnet, so a /24; 4 x 2 = 8 subnets x 256 = 2048, so a /21
#   aws-europe: 150 x 3 + 5 = 455 addresses a subnet, so a /23; 6 x 2 = 12 subnets x 512 = 6144, so a /19
#   aws-asia: 40 x 3 + 5 = 125 addresses a subnet, so a /25; 3 x 2 = 6 subnets x 128 = 768, so a /22
#   aws: its regions take 27648; twice that is 55296, so the summary is a /16
#   azure-us-east: 200 x 3 + 5 = 605 addresses a subnet, so a /22; 4 x 2 = 8 subnets x 1024 = 8192, so a /19
#   azure-us-west: 170 x 3 + 5 = 515 addresses a subnet, so a /22; 4 x 2 = 8 subnets x 1024 = 8192, so a /19
#   azure-europe: 100 x 3 + 5 = 305 addresses a subnet, so a /23; 8 x 2 = 16 subnets x 512 = 8192, so a /19
#   azure-asia: 60 x 3 + 5 = 185 addresses a subnet, so a /24; 2 x 2 = 4 subnets x 256 = 1024, so a /22
#   azure: its regions take 25600; twice that is 51200, so the summary is a /16
#   gcp-us-east: 250 x 3 + 4 = 754 addresses a subnet, so a /22; 4 x 2 = 8 subnets x 1024 = 8192, so a /19
#   gcp-us-west: 100 x 3 + 4 = 304 addresses a subnet, so a /23; 2 x 2 = 4 subnets x 512 = 2048, so a /21
#   gcp-europe: 120 x 3 + 4 = 364 addresses a subnet, so a /23; 4 x 2 = 8 subnets x 512 = 4096, so a /20
#   gcp-asia: 500 x 3 + 4 = 1504 addresses a subnet, so a /21; 3 x 2 = 6 subnets x 2048 = 12288, so a /18
#   gcp: its regions take 30720; twice that is 61440, so the summary is a /16
#   onprem: 10.0.0.0/16 and 10.1.0.0/16 differ in the second number's
#   last bit, so the smallest block holding both is 10.0.0.0/15.
# The summaries go where nothing is in use (10.0 and 10.1 are the data
# centres, 10.100 the partner, 10.255 the old lab), each region inside
# its summary, biggest first, each on a multiple of its own size.
# IPv6: a /44 for each summary from the shop's /40, a /48 for each site
# inside its summary; Google Cloud's network is a /48 from fd20::/20, and
# its regions' /64s are its to pick, so they are -.
cat > ~/plan/plan.csv <<'EOF'
name,ipv4,ipv6
aws,10.2.0.0/16,2001:db8:4800::/44
aws-us-east,10.2.0.0/18,2001:db8:4800::/48
aws-us-west,10.2.96.0/21,2001:db8:4801::/48
aws-europe,10.2.64.0/19,2001:db8:4802::/48
aws-asia,10.2.104.0/22,2001:db8:4803::/48
azure,10.3.0.0/16,2001:db8:4810::/44
azure-us-east,10.3.0.0/19,2001:db8:4810::/48
azure-us-west,10.3.32.0/19,2001:db8:4811::/48
azure-europe,10.3.64.0/19,2001:db8:4812::/48
azure-asia,10.3.96.0/22,2001:db8:4813::/48
gcp,10.4.0.0/16,fd20:a7b:9c00::/48
gcp-us-east,10.4.64.0/19,-
gcp-us-west,10.4.112.0/21,-
gcp-europe,10.4.96.0/20,-
gcp-asia,10.4.0.0/18,-
onprem,10.0.0.0/15,2001:db8:48f0::/44
dc-dallas,10.0.0.0/16,2001:db8:48f0::/48
dc-london,10.1.0.0/16,2001:db8:48f1::/48
EOF
plan-show
