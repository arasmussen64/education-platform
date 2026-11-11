# Wrong: c3 kept on its A10G card, which fits at twice the price of a T4
# that fits too.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
c1,n4-standard-2,66.21
c2,r7i.large,514.14
c3,g5.xlarge,90.54
saving,,1040.25
EOF
