# Wrong: AWS's summary is the smallest block that holds its subnets,
# 10.64.0.0/20 (4,096 addresses for 4,032 used), with no room beside them:
# the next zone or tier added can't fit inside it.
mkdir -p ~/plan
cat > ~/plan/plan.txt << 'EOF'
aws-a-web   10.64.0.0/22
aws-b-web   10.64.4.0/22
aws-c-web   10.64.8.0/22
aws-a-app   10.64.12.0/24
aws-b-app   10.64.13.0/24
aws-c-app   10.64.14.0/24
aws-a-data  10.64.15.0/26
aws-b-data  10.64.15.64/26
aws-c-data  10.64.15.128/26
az-web      10.64.32.0/22
az-app      10.64.36.0/25
az-data     10.64.36.128/27
gcp-web     10.64.48.0/25
gcp-app     10.64.48.128/26
gcp-data    10.64.48.192/28
EOF
cat > ~/plan/summary.txt << 'EOF'
aws     10.64.0.0/20
azure   10.64.32.0/20
gcp     10.64.48.0/23
EOF
