# Wrong: a profile's first number read as its memory slices too.
# 3g.20gb takes 3 compute slices but 4 memory slices (20 GB), so two of
# them and a 1g.5gb need 9 memory slices, not 7.
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
valid-layouts=2,3,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
