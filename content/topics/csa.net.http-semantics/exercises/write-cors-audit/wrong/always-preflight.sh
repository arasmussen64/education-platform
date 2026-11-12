# Wrong: it sends a preflight for every request, simple ones too, and
# refuses a simple GET whose preflight answer it never needed.
cat > ~/bin/cors-audit << 'EOF'
#!/bin/bash
# cors-audit URL ORIGIN METHOD [HEADER] [--credentials]: what a browser
# decides about one request from a page on ORIGIN to URL, from the server's
# own answers: "allowed", or "blocked:" and the reason. HEADER is the one
# header the page adds ("Name: value"); --credentials sends the customer's
# cookie, as credentials: "include" does.
set -euo pipefail

credentials=no
args=()
for arg in "$@"; do
  if [ "$arg" = --credentials ]; then credentials=yes; else args+=("$arg"); fi
done
url=${args[0]}
origin=${args[1]}
method=${args[2]}
header=${args[3]:-}

# header_value ANSWER NAME: the value of header NAME in ANSWER (what curl
# -si printed), whatever the case of its name, or nothing.
header_value() {
  printf '%s\n' "$1" | tr -d '\r' | awk -v want="$2" '
    found == 0 && tolower(substr($0, 1, length(want) + 1)) == tolower(want) ":" {
      value = substr($0, length(want) + 2); sub(/^ +/, "", value); print value; found = 1 }'
}

# has LIST ITEM: whether ITEM is one of LIST's comma-separated items
# (LIST without spaces): ",GET,PUT," holds ",PUT,".
has() {
  case ",$1," in *",$2,"*) return 0 ;; esac
  return 1
}

# cors_check ANSWER: the CORS check on one answer; prints the reason it
# fails, or nothing.
cors_check() {
  local allowed
  allowed=$(header_value "$1" Access-Control-Allow-Origin)
  if [ -z "$allowed" ]; then
    echo "no allow-origin"
  elif [ "$allowed" = "*" ]; then
    if [ "$credentials" = yes ]; then echo "wildcard with credentials"; fi
  elif [ "$allowed" != "$origin" ]; then
    echo "origin not allowed"
  elif [ "$credentials" = yes ] && [ "$(header_value "$1" Access-Control-Allow-Credentials)" != true ]; then
    echo "credentials not allowed"
  fi
}

# Is it a simple request? A safelisted method, and no header beyond the
# safelisted ones.
simple_method=no
case $method in GET | HEAD | POST) simple_method=yes ;; esac
name=$(echo "${header%%:*}" | tr '[:upper:]' '[:lower:]')
value=$(echo "${header#*:}" | tr -d ' ' | cut -d ';' -f 1 | tr '[:upper:]' '[:lower:]')
safe_header=yes
if [ -n "$header" ]; then
  case $name in
    accept | accept-language | content-language) ;;
    content-type)
      case $value in
        application/x-www-form-urlencoded | multipart/form-data | text/plain) ;;
        *) safe_header=no ;;
      esac
      ;;
    *) safe_header=no ;;
  esac
fi

# Not simple: the preflight first, as the browser sends it (no cookie).
if [ "$simple_method" != never ]; then
  ask=(-H "Origin: $origin" -H "Access-Control-Request-Method: $method")
  if [ "$safe_header" = no ]; then ask+=(-H "Access-Control-Request-Headers: $name"); fi
  answer=$(curl -si --max-time 5 -X OPTIONS "${ask[@]}" "$url")
  reason=$(cors_check "$answer")
  if [ -n "$reason" ]; then
    echo "blocked: $reason"
    exit 0
  fi
  methods=$(header_value "$answer" Access-Control-Allow-Methods | tr -d ' ')
  if [ "$simple_method" = no ] && ! has "$methods" "$method"; then
    if [ "$credentials" = yes ] || ! has "$methods" "*"; then
      echo "blocked: method not allowed"
      exit 0
    fi
  fi
  names=$(header_value "$answer" Access-Control-Allow-Headers | tr -d ' ' | tr '[:upper:]' '[:lower:]')
  if [ "$safe_header" = no ] && ! has "$names" "$name"; then
    if [ "$credentials" = yes ] || ! has "$names" "*"; then
      echo "blocked: header not allowed"
      exit 0
    fi
  fi
fi

# The request itself, and the CORS check on its answer.
send=(-X "$method" -H "Origin: $origin")
if [ -n "$header" ]; then send+=(-H "$header"); fi
if [ "$credentials" = yes ]; then send+=(-H "Cookie: session=audit"); fi
answer=$(curl -si --max-time 5 "${send[@]}" "$url")
reason=$(cors_check "$answer")
if [ -n "$reason" ]; then
  echo "blocked: $reason"
else
  echo allowed
fi
EOF
chmod +x ~/bin/cors-audit
