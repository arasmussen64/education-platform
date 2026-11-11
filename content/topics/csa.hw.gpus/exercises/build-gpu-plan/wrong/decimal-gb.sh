# Wrong: the weights worked in GB of a thousand million bytes, not GiB:
# 22.00 for chat and 48.00 for tune, about 7% too much. (The instances
# come out the same here; the sizes don't.)
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=22.00
instance.chat=g6e.xlarge
monthly.chat=1358.53
needed-gib.tune=48.00
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
