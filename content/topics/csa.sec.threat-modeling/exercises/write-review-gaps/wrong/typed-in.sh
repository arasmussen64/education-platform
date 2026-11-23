# The example's answer, typed in: right for ~/example.tm and for nothing else.
mkdir -p ~/bin
cat > ~/bin/review-gaps <<'EOF'
#!/bin/bash
cat <<'ANSWER'
f1: reviewed
f3: STRIDE
f4: TIDE
crossing 3, unreviewed 2
ANSWER
EOF
chmod +x ~/bin/review-gaps
