# Wrong: Google is given AWS's and Azure's 5 reserved addresses. Google
# keeps 4, so its web subnet needs 2 x 62 + 4 = 128, which a /25 holds
# exactly; with 5 it would need 129 and a /24. Its three subnets are each
# one size too big (and its summary grows to match).
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
gcp-web     10.64.48.0/24
gcp-app     10.64.49.0/25
gcp-data    10.64.49.128/27
EOF
cat > ~/plan/summary.txt << 'EOF'
aws     10.64.0.0/19
azure   10.64.32.0/20
gcp     10.64.48.0/22
EOF
