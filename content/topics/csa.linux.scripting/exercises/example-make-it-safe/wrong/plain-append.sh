# Wrong: the append has no guard, so running the loop twice writes the line
# twice and runs.txt has two lines.
mkdir -p ~/example
line="deployed"; file=~/example/runs.txt; : > "$file"
for run in 1 2; do echo "$line" >> "$file"; done
{ echo "idempotent-lines: $(wc -l < ~/example/runs.txt | tr -d ' ')"; echo "set-u-stops: yes"; } > ~/example/notes.txt
