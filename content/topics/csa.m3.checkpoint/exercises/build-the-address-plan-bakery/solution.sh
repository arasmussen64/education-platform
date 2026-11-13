# A reference, one layout among many: the checks hold rules, not answers.
# The arithmetic (README rules 2, 4 and 5), then the plan, written whole.
# cat > FILE <<'EOF' writes the lines up to EOF into FILE.
cat /srv/plan/README.txt /srv/plan/sites.csv /srv/plan/policy.txt
#   aws-us-east: 100 x 3 + 5 = 305 addresses a subnet, so a /23; 3 x 2 = 6 subnets x 512 = 3072, so a /20
#   aws-us-west: 40 x 3 + 5 = 125 addresses a subnet, so a /25; 2 x 2 = 4 subnets x 128 = 512, so a /23
#   aws-europe: 70 x 3 + 5 = 215 addresses a subnet, so a /24; 4 x 2 = 8 subnets x 256 = 2048, so a /21
#   aws-asia: 25 x 3 + 5 = 80 addresses a subnet, so a /25; 2 x 2 = 4 subnets x 128 = 512, so a /23
#   aws: its regions take 7168; twice that is 14336, so the summary is a /18
#   azure-us-east: 150 x 3 + 5 = 455 addresses a subnet, so a /23; 2 x 2 = 4 subnets x 512 = 2048, so a /21
#   azure-us-west: 42 x 3 + 5 = 131 addresses a subnet, so a /24; 2 x 2 = 4 subnets x 256 = 1024, so a /22
#   azure-europe: 95 x 3 + 5 = 290 addresses a subnet, so a /23; 3 x 2 = 6 subnets x 512 = 3072, so a /20
#   azure-asia: 25 x 3 + 5 = 80 addresses a subnet, so a /25; 2 x 2 = 4 subnets x 128 = 512, so a /23
#   azure: its regions take 7680; twice that is 15360, so the summary is a /18
#   gcp-us-east: 60 x 3 + 4 = 184 addresses a subnet, so a /24; 4 x 2 = 8 subnets x 256 = 2048, so a /21
#   gcp-us-west: 15 x 3 + 4 = 49 addresses a subnet, so a /26; 2 x 2 = 4 subnets x 64 = 256, so a /24
#   gcp-europe: 130 x 3 + 4 = 394 addresses a subnet, so a /23; 3 x 2 = 6 subnets x 512 = 3072, so a /20
#   gcp-asia: 50 x 3 + 4 = 154 addresses a subnet, so a /24; 2 x 2 = 4 subnets x 256 = 1024, so a /22
#   gcp: its regions take 7424; twice that is 14848, so the summary is a /18
cat > ~/plan/plan.csv <<'EOF'
name,ipv4,ipv6
aws,172.16.0.0/18,2001:db8:9e00::/44
aws-us-east,172.16.0.0/20,2001:db8:9e00::/48
aws-us-west,172.16.24.0/23,2001:db8:9e01::/48
aws-europe,172.16.16.0/21,2001:db8:9e02::/48
aws-asia,172.16.26.0/23,2001:db8:9e03::/48
azure,172.16.64.0/18,2001:db8:9e10::/44
azure-us-east,172.16.80.0/21,2001:db8:9e10::/48
azure-us-west,172.16.88.0/22,2001:db8:9e11::/48
azure-europe,172.16.64.0/20,2001:db8:9e12::/48
azure-asia,172.16.92.0/23,2001:db8:9e13::/48
gcp,172.16.128.0/18,fd20:e04:7700::/48
gcp-us-east,172.16.144.0/21,-
gcp-us-west,172.16.156.0/24,-
gcp-europe,172.16.128.0/20,-
gcp-asia,172.16.152.0/22,-
onprem,172.18.0.0/15,2001:db8:9ef0::/44
dc-york,172.18.0.0/16,2001:db8:9ef0::/48
dc-cardiff,172.19.0.0/16,2001:db8:9ef1::/48
EOF
plan-show
