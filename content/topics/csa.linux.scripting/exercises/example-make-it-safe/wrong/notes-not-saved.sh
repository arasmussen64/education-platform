# Wrong: the idempotent file is made correctly, but the notes were never
# saved, so the facts the checks read back aren't there.
mkdir -p ~/example
line="deployed"; file=~/example/runs.txt; : > "$file"
for run in 1 2; do grep -qxF "$line" "$file" || echo "$line" >> "$file"; done
