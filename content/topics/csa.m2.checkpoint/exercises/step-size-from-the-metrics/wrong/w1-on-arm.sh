# Wrong: w1 on the Arm size a little cheaper, though its vendor agent runs
# only on x86.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,c4a-standard-4,131.11
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,1784.25
EOF
