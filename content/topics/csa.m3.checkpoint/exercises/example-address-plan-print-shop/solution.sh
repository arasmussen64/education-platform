# A worked example: the print shop's address plan, two clouds with two
# regions each and one data centre, in the order the checkpoint's build
# needs. Type each line and read what it prints; the # lines say what the
# numbers mean. cat > FILE <<'EOF' writes the lines up to EOF into FILE.

cat /srv/plan/README.txt
cat /srv/plan/sites.csv /srv/plan/policy.txt

# machines x host_growth + the cloud's reserved addresses, up to a power of two
#   aws-us-east: 100 x 3 + 5 = 305, so 512 addresses
#   aws-europe:   60 x 3 + 5 = 185, so 256
#   gcp-us-east: 150 x 3 + 4 = 454, so 512
#   gcp-europe:   40 x 3 + 4 = 124, so 128
ipcalc -b 10.0.0.0/23

# twice today's subnets (subnet_growth), each the size above, up to a power of two
#   aws-us-east: 4 x 2 =  8 subnets x 512 = 4096, a /20
#   aws-europe:  2 x 2 =  4 subnets x 256 = 1024, a /22
#   gcp-us-east: 3 x 2 =  6 subnets x 512 = 3072, so 4096, a /20
#   gcp-europe:  2 x 2 =  4 subnets x 128 =  512, a /23

# twice what its regions take (summary_room), up to a power of two
#   aws: 4096 + 1024 = 5120, x 2 = 10240, so 16384, a /18
#   gcp: 4096 +  512 = 4608, x 2 =  9216, so 16384, a /18

#   aws  10.0.0.0/18:  aws-us-east 10.0.0.0/20,  aws-europe 10.0.16.0/22
#   gcp  10.0.64.0/18: gcp-us-east 10.0.64.0/20, gcp-europe 10.0.80.0/23
ipcalc -b 10.0.64.0/18

#   dc-main 10.50.0.0/16, as it is; onprem, the smallest block holding it: 10.50.0.0/16

#   aws: 2001:db8:7700::/44, its regions 2001:db8:7700::/48 and 2001:db8:7701::/48
#   onprem: 2001:db8:77f0::/44, dc-main 2001:db8:77f0::/48
#   gcp: fd20:5b2:1000::/48, a /48 from fd20::/20; its regions -
sipcalc 2001:db8:7700::/44

cat > ~/plan/plan.csv <<'EOF'
name,ipv4,ipv6
aws,10.0.0.0/18,2001:db8:7700::/44
aws-us-east,10.0.0.0/20,2001:db8:7700::/48
aws-europe,10.0.16.0/22,2001:db8:7701::/48
gcp,10.0.64.0/18,fd20:5b2:1000::/48
gcp-us-east,10.0.64.0/20,-
gcp-europe,10.0.80.0/23,-
onprem,10.50.0.0/16,2001:db8:77f0::/44
dc-main,10.50.0.0/16,2001:db8:77f0::/48
EOF
plan-show
