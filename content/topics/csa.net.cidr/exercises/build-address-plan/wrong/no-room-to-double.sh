# Wrong: each subnet is sized for its machines today plus the reserved
# addresses, with no room for them to double: AWS's web subnets get a /23
# for 254 + 5 = 259, where twice the machines need a /22.
mkdir -p ~/plan
cat > ~/plan/plan.txt << 'EOF'
aws-a-web   10.64.0.0/23
aws-b-web   10.64.2.0/23
aws-c-web   10.64.4.0/23
aws-a-app   10.64.6.0/25
aws-b-app   10.64.6.128/25
aws-c-app   10.64.7.0/25
aws-a-data  10.64.7.128/27
aws-b-data  10.64.7.160/27
aws-c-data  10.64.7.192/27
az-web      10.64.32.0/22
az-app      10.64.36.0/25
az-data     10.64.36.128/27
gcp-web     10.64.48.0/25
gcp-app     10.64.48.128/26
gcp-data    10.64.48.192/28
EOF
cat > ~/plan/summary.txt << 'EOF'
aws     10.64.0.0/19
azure   10.64.32.0/20
gcp     10.64.48.0/23
EOF
