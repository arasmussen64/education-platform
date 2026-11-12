# Wrong: the script sends the two requests and hands the decision to the
# checks' own model of a browser, found in /usr/local/lib/lab, so it is
# right every time and the learner has written no rule at all.
cat > ~/bin/cors-audit << 'EOF'
#!/bin/bash
# cors-audit URL ORIGIN METHOD [HEADER] [--credentials]
set -euo pipefail
dir=$(mktemp -d)
cred=()
header=()
for arg in "${@:4}"; do
  if [ "$arg" = --credentials ]; then cred=(--credentials); else header=("$arg"); fi
done
curl -si -X OPTIONS -H "Origin: $2" -H "Access-Control-Request-Method: $3" "$1" > "$dir/pre"
curl -si -X "$3" -H "Origin: $2" "$1" > "$dir/act"
python3 /usr/local/lib/lab/cors-verdict "$dir/pre" "$dir/act" "$2" "$3" "${header[@]}" "${cred[@]}"
rm -rf "$dir"
EOF
chmod +x ~/bin/cors-audit
