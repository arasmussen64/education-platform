# Wrong: each subnet is sized for twice its machines and nothing else. AWS
# keeps 5 addresses of every subnet, so a web subnet needs 2 x 254 + 5 =
# 513, one more than a /23 holds. (Everywhere else the reserved addresses
# happen to fit in the same size.)
mkdir -p ~/plan
cat > ~/plan/plan.txt << 'EOF'
aws-a-web   10.64.0.0/23
aws-b-web   10.64.2.0/23
aws-c-web   10.64.4.0/23
aws-a-app   10.64.6.0/24
aws-b-app   10.64.7.0/24
aws-c-app   10.64.8.0/24
aws-a-data  10.64.9.0/26
aws-b-data  10.64.9.64/26
aws-c-data  10.64.9.128/26
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
