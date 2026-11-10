mkdir -p ~/example
( set -u; BUILD_DIR=/srv/app/build; echo "would clean ${BUILD_DRI}/" ) 2>&1 | head -1; echo "set-u exit: ${PIPESTATUS[0]}"
( BUILD_DIR=/srv/app/build; echo "would clean ${BUILD_DRI}/" )
( set -o pipefail; cat /no/such/file 2>/dev/null | wc -l >/dev/null; echo "pipefail exit: $?" ); ( cat /no/such/file 2>/dev/null | wc -l >/dev/null; echo "no-pipefail exit: $?" )
name="my report.txt"; if [[ -n "$name" ]]; then echo "one name: [$name]"; fi
bash -c 'set -e; tmp=$(mktemp -d); trap "rm -rf \"$tmp\"; echo cleaned: \"$tmp\"" EXIT; echo "working in $tmp"; false; echo "this never prints"'; echo "the temp dir is gone, because the trap ran"
line="deployed"; file=~/example/runs.txt; : > "$file"; for run in 1 2; do grep -qxF "$line" "$file" || echo "$line" >> "$file"; done; echo "after two runs, lines: $(wc -l < "$file")"
{ echo "idempotent-lines: $(wc -l < ~/example/runs.txt | tr -d ' ')"; echo "set-u-stops: yes"; } > ~/example/notes.txt
cat ~/example/notes.txt
