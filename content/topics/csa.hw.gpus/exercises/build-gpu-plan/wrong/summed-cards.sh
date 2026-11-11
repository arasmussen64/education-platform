# Wrong: the g6.12xlarge's four cards counted as one of 88 GiB. A job that
# runs on one card gets one card's 22 GiB, and tune needs 44.70.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g6e.xlarge
monthly.chat=1358.53
needed-gib.tune=44.70
instance.tune=NC24ads_A100_v4
job-cost.tune=33.06
tune-fits.g6.12xlarge=yes
cards-needed.big-16bit=3
cards-needed.big-4bit=1
cards.embed=2
valid-layouts=2,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
