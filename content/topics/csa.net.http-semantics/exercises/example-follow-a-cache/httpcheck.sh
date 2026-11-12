# httpcheck.sh: the HTTP semantics labs' check helpers, beside the base's.
# A check starts with:   . /usr/local/lib/lab/httpcheck.sh
# Every request is made from the office, as a customer's browser would make
# it, through the edge cache (www.shop.test) unless a check names the
# origin (origin.shop.test).
. /usr/local/lib/netlab/checklib.sh

# fresh: a query string no request has used yet, so the edge has no copy
# of the page it is added to (the edge keys its copies on the whole URL).
fresh() { echo "check=$(date +%s%N)$RANDOM"; }

# headers URL [CURL OPTIONS...]: the status line and headers of the answer.
headers() { on office curl -s -o /dev/null -D - --max-time 5 "$@" 2> /dev/null | tr -d '\r'; }

# page URL [CURL OPTIONS...]: the body of the answer.
page() { on office curl -s --max-time 5 "$@" 2> /dev/null; }

# header NAME: the value of header NAME in the headers on stdin, whatever
# its case, repeated headers joined with ", ".
header() {
  awk -v want="$(echo "$1" | tr '[:upper:]' '[:lower:]')" '
    index($0, ":") { name = tolower(substr($0, 1, index($0, ":") - 1))
                     value = substr($0, index($0, ":") + 1); sub(/^ +/, "", value)
                     if (name == want) all = all (all == "" ? "" : ", ") value }
    END { print all }'
}

# version: the price list's version number in the page on stdin.
version() { grep -o 'Prices version [0-9]*' | grep -o '[0-9]*$'; }

# cors DIR ORIGIN METHOD [HEADER] [--credentials]: what a browser on a page
# from ORIGIN decides about METHOD on the basket API, through the edge: the
# preflight and the request a browser would send, kept in DIR/pre and
# DIR/act, then cors-verdict, the base's model of the browser, on the two
# answers. With --credentials the request carries a customer's cookie, as
# credentials: "include" does.
cors() {
  local dir=$1 origin=$2 method=$3 header="" cred="" arg
  shift 3
  for arg in "$@"; do
    if [[ $arg == --credentials ]]; then cred=--credentials; else header=$arg; fi
  done
  local ask=(-H "Origin: $origin" -H "Access-Control-Request-Method: $method")
  [[ -n $header ]] && ask+=(-H "Access-Control-Request-Headers: $(echo "${header%%:*}" | tr '[:upper:]' '[:lower:]')")
  on office curl -si --max-time 5 -X OPTIONS "${ask[@]}" http://www.shop.test/api/basket > "$dir/pre" 2> /dev/null
  local send=(-X "$method" -H "Origin: $origin")
  [[ -n $header ]] && send+=(-H "$header")
  [[ -n $cred ]] && send+=(-H "Cookie: session=cara")
  [[ $method == PUT ]] && send+=(--data '{"items": 2}')
  on office curl -si --max-time 5 "${send[@]}" http://www.shop.test/api/basket > "$dir/act" 2> /dev/null
  python3 /usr/local/lib/netlab/cors-verdict "$dir/pre" "$dir/act" "$origin" "$method" ${header:+"$header"} $cred
}
