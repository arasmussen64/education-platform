# Wrong: box-4 judged by its card alone. At about a quarter busy with
# its data disk at 100% and the CPUs waiting on reads, the card is
# starved by the disk; "none" is box-5's verdict, not box-4's.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g6e.xlarge
monthly.chat=1358.53
needed-gib.tune=44.70
instance.tune=NC24ads_A100_v4
job-cost.tune=33.06
tune-fits.g6.12xlarge=no
cards-needed.big-16bit=3
cards-needed.big-4bit=1
cards.embed=2
valid-layouts=2,4
starved-by.box-4=none
starved-by.box-5=none
avg-util.box-4=23.6
EOF
