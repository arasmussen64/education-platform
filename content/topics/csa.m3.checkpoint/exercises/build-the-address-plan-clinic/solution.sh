# A reference, one layout among many: the checks hold rules, not answers.
# The arithmetic (README rules 2, 4 and 5), then the plan, written whole.
# cat > FILE <<'EOF' writes the lines up to EOF into FILE.
cat /srv/plan/README.txt /srv/plan/sites.csv /srv/plan/policy.txt
#   aws-us-east: 120 x 3 + 5 = 365 addresses a subnet, so a /23; 4 x 2 = 8 subnets x 512 = 4096, so a /20
#   aws-us-west: 300 x 3 + 5 = 905 addresses a subnet, so a /22; 2 x 2 = 4 subnets x 1024 = 4096, so a /20
#   aws-europe: 60 x 3 + 5 = 185 addresses a subnet, so a /24; 8 x 2 = 16 subnets x 256 = 4096, so a /20
#   aws-asia: 25 x 3 + 5 = 80 addresses a subnet, so a /25; 2 x 2 = 4 subnets x 128 = 512, so a /23
#   aws: its regions take 12800; twice that is 25600, so the summary is a /17
#   azure-us-east: 95 x 3 + 5 = 290 addresses a subnet, so a /23; 6 x 2 = 12 subnets x 512 = 6144, so a /19
#   azure-us-west: 40 x 3 + 5 = 125 addresses a subnet, so a /25; 3 x 2 = 6 subnets x 128 = 768, so a /22
#   azure-europe: 400 x 3 + 5 = 1205 addresses a subnet, so a /21; 4 x 2 = 8 subnets x 2048 = 16384, so a /18
#   azure-asia: 150 x 3 + 5 = 455 addresses a subnet, so a /23; 2 x 2 = 4 subnets x 512 = 2048, so a /21
#   azure: its regions take 27648; twice that is 55296, so the summary is a /16
#   gcp-us-east: 70 x 3 + 4 = 214 addresses a subnet, so a /24; 5 x 2 = 10 subnets x 256 = 2560, so a /20
#   gcp-us-west: 30 x 3 + 4 = 94 addresses a subnet, so a /25; 2 x 2 = 4 subnets x 128 = 512, so a /23
#   gcp-europe: 85 x 3 + 4 = 259 addresses a subnet, so a /23; 3 x 2 = 6 subnets x 512 = 3072, so a /20
#   gcp-asia: 200 x 3 + 4 = 604 addresses a subnet, so a /22; 2 x 2 = 4 subnets x 1024 = 4096, so a /20
#   gcp: its regions take 12800; twice that is 25600, so the summary is a /17
cat > ~/plan/plan.csv <<'EOF'
name,ipv4,ipv6
aws,10.1.0.0/17,2001:db8:6100::/44
aws-us-east,10.1.0.0/20,2001:db8:6100::/48
aws-us-west,10.1.16.0/20,2001:db8:6101::/48
aws-europe,10.1.32.0/20,2001:db8:6102::/48
aws-asia,10.1.48.0/23,2001:db8:6103::/48
azure,10.0.0.0/16,2001:db8:6110::/44
azure-us-east,10.0.64.0/19,2001:db8:6110::/48
azure-us-west,10.0.104.0/22,2001:db8:6111::/48
azure-europe,10.0.0.0/18,2001:db8:6112::/48
azure-asia,10.0.96.0/21,2001:db8:6113::/48
gcp,10.1.128.0/17,fd20:3c1:5e00::/48
gcp-us-east,10.1.128.0/20,-
gcp-us-west,10.1.176.0/23,-
gcp-europe,10.1.144.0/20,-
gcp-asia,10.1.160.0/20,-
onprem,10.10.0.0/15,2001:db8:61f0::/44
dc-leeds,10.10.0.0/16,2001:db8:61f0::/48
dc-bristol,10.11.0.0/16,2001:db8:61f1::/48
EOF
plan-show
