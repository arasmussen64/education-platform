# Wrong: the six services counted by memory alone: 6 x 6 GB is 36 GB,
# which one A100 40GB holds. But they must not disturb one another, so
# each needs a MIG instance of its own, and the smallest that holds 6 GB
# is a 10 GB profile: four to a card.
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
cards.embed=1
valid-layouts=2,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
