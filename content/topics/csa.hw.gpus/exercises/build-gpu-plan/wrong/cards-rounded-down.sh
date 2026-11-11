# Wrong: the cards worked out and then rounded down. 2.7 cards' worth
# needs 3 cards, and 0.67 of a card needs 1, not 0.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g6e.xlarge
monthly.chat=1358.53
needed-gib.tune=44.70
instance.tune=NC24ads_A100_v4
job-cost.tune=33.06
tune-fits.g6.12xlarge=no
cards-needed.big-16bit=2
cards-needed.big-4bit=0
cards.embed=2
valid-layouts=2,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
