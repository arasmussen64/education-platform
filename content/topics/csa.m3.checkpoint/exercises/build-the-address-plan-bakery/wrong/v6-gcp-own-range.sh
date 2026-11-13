# Wrong: Google Cloud's network is given a block from the bakery's own /40.
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
gcp,172.16.128.0/18,2001:db8:9e20::/48
gcp-us-east,172.16.144.0/21,-
gcp-us-west,172.16.156.0/24,-
gcp-europe,172.16.128.0/20,-
gcp-asia,172.16.152.0/22,-
onprem,172.18.0.0/15,2001:db8:9ef0::/44
dc-york,172.18.0.0/16,2001:db8:9ef0::/48
dc-cardiff,172.19.0.0/16,2001:db8:9ef1::/48
EOF
