# Wrong: c1 moved to Arm, though the insurer's agent runs only on x86.
cat > ~/sizing/answers.csv <<'EOF'
workload,instance,monthly_usd
c1,c4a-standard-2,65.55
c2,r7i.large,514.14
c3,NC4as_T4_v3,47.34
saving,,1084.11
EOF
