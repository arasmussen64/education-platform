# Wrong: w1 sized on its averages (about 10% of 8 vCPUs and 8.5 GiB): 2
# vCPUs and 16 GiB, too few vCPUs for its busy hours.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-highmem-2,86.88
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1828.48
EOF
