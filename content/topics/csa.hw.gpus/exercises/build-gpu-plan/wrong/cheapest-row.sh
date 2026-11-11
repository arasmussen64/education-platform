# Wrong: the cheapest row in the table for both jobs, whatever its card
# holds. A T4's 16 GiB holds neither chat with its headroom nor tune.
cat > ~/plan/answers.txt <<'EOF'
weights-gib.chat=20.49
instance.chat=g4dn.xlarge
monthly.chat=383.98
needed-gib.tune=44.70
instance.tune=g4dn.xlarge
job-cost.tune=4.73
tune-fits.g6.12xlarge=no
cards-needed.big-16bit=3
cards-needed.big-4bit=1
cards.embed=2
valid-layouts=2,4
starved-by.box-4=disk
starved-by.box-5=none
avg-util.box-4=23.6
EOF
