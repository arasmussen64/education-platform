# Wrong: the script works out each subnet's groups itself, but hands the
# short form to sipcalc, one run for every line, and prints its
# "Compressed address". Every line is right and ShellCheck is quiet, but
# the short form, half of what the script is for, isn't the learner's.
mkdir -p ~/bin
cat > ~/bin/v6-plan << 'EOF'
#!/bin/bash
set -euo pipefail
p=${1%/*}
p=${p%::}
IFS=: read -r g1 g2 g3 <<< "$p"
for (( r = 0; r < $2; r++ )); do
  for (( z = 0; z < $3; z++ )); do
    for (( t = 0; t < $4; t++ )); do
      full="$g1:${g2:-0}:${g3:-0}:$(printf '%x%x%02x' "$r" "$z" "$t")::"
      short=$(sipcalc "$full/64" | awk '/^Compressed address/ {print $NF}')
      printf 'r%x-z%x-t%02x %s/64\n' "$r" "$z" "$t" "$short"
    done
  done
done
EOF
chmod +x ~/bin/v6-plan
