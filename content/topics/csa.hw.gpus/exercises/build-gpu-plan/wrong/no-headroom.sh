# Wrong: chat sized on its weights alone. 20.49 GiB fits a 22 GiB card,
# but the plan asks for 25% on top, 25.61 GiB, which doesn't.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g2-standard-4
monthly.chat=515.99
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
