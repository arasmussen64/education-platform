# Wrong: w2 put on a GPU size because it has the vCPUs and the memory and
# lands within 15% of the cheapest: NC8as_T4_v3, 8 vCPUs and 56 GiB, at
# $1,401.60 with both licences. The database never uses the T4 card it pays
# for.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,NC8as_T4_v3,1401.60
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1601.90
EOF
