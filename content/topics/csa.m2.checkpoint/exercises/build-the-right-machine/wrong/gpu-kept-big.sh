# Wrong: w4 kept on its A100: it fits, at five times the price of a card
# that is big enough.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
w1,n4-standard-4,132.42
w2,E8s_v5,1220.56
w3,m7g.xlarge,119.14
w4,NC24ads_A100_v4,661.14
w5,B2ls_v2,30.37
saving,,1249.03
EOF
