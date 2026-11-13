# Wrong: Google Cloud's network is given a block from the print shop's own /40.
cat > ~/plan/plan.csv <<'EOF'
name,ipv4,ipv6
aws,10.0.0.0/18,2001:db8:7700::/44
aws-us-east,10.0.0.0/20,2001:db8:7700::/48
aws-europe,10.0.16.0/22,2001:db8:7701::/48
gcp,10.0.64.0/18,2001:db8:7710::/48
gcp-us-east,10.0.64.0/20,-
gcp-europe,10.0.80.0/23,-
onprem,10.50.0.0/16,2001:db8:77f0::/44
dc-main,10.50.0.0/16,2001:db8:77f0::/48
EOF
