# Wrong: a month of 720 hours (30 days). The plan's month is 730 hours,
# and the difference, about 1.4%, is more than the check allows.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g6e.xlarge
monthly.chat=1339.92
needed-gib.tune=44.70
instance.tune=NC24ads_A100_v4
job-cost.tune=33.06
tune-fits.g6.12xlarge=no
cards-needed.big-16bit=3
cards-needed.big-4bit=1
cards.embed=2
valid-layouts=2,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
