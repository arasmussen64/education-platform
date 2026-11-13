# Wrong: gcp-europe's subnets are sized without the 4 addresses Google Cloud keeps back (255 fits in 256; 259 doesn't).
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
gcp-europe,10.1.144.0/21,-
gcp-asia,10.1.160.0/20,-
onprem,10.10.0.0/15,2001:db8:61f0::/44
dc-leeds,10.10.0.0/16,2001:db8:61f0::/48
dc-bristol,10.11.0.0/16,2001:db8:61f1::/48
EOF
