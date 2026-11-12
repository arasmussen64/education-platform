# Wrong: w2 sized on CPU alone: D8s_v5 has the vCPUs, and 32 GiB for a peak
# of 41.3.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,D8s_v5,1132.96
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1870.54
EOF
