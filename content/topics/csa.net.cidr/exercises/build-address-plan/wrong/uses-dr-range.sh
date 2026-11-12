# Wrong: Azure's subnets are drawn from 10.72.0.0/16, a free-looking /16
# inside the company's 10.64.0.0/12, but it is the disaster-recovery
# site's range, which the plan must not touch.
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
az-web      10.72.0.0/22
az-app      10.72.4.0/25
az-data     10.72.4.128/27
gcp-web     10.64.48.0/25
gcp-app     10.64.48.128/26
gcp-data    10.64.48.192/28
EOF
cat > ~/plan/summary.txt << 'EOF'
aws     10.64.0.0/19
azure   10.72.0.0/20
gcp     10.64.48.0/23
EOF
