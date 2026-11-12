# Wrong: the right sizes, but w2 costed with Windows Server and without SQL
# Server Standard.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,636.56
w3,m7g.xlarge,119.14
w4,g2-standard-4,127.23
w5,B2ls_v2,30.37
saving,,2366.94
EOF
