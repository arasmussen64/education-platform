# Wrong: azure-asia's IPv6 block is azure-europe's.
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
azure-asia,10.3.96.0/22,2001:db8:4812::/48
gcp,10.4.0.0/16,fd20:a7b:9c00::/48
gcp-us-east,10.4.64.0/19,-
gcp-us-west,10.4.112.0/21,-
gcp-europe,10.4.96.0/20,-
gcp-asia,10.4.0.0/18,-
onprem,10.0.0.0/15,2001:db8:48f0::/44
dc-dallas,10.0.0.0/16,2001:db8:48f0::/48
dc-london,10.1.0.0/16,2001:db8:48f1::/48
EOF
