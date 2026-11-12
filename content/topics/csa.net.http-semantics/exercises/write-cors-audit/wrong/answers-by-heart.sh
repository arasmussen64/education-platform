# Wrong: the script knows the shop's own rules by heart and asks nobody:
# the shop's two sites may use GET, PUT and DELETE, and nothing else is
# allowed. Right about the shop's API, and wrong about every other.
cat > ~/bin/cors-audit << 'EOF'
#!/bin/bash
# cors-audit URL ORIGIN METHOD [HEADER] [--credentials]: the shop's rules.
set -euo pipefail
origin=$2
method=$3
header=${4:-}
case $origin in
  https://shop.test | https://www.shop.test) ;;
  *)
    echo "blocked: no allow-origin"
    exit 0
    ;;
esac
case $method in
  GET | PUT | DELETE) ;;
  *)
    echo "blocked: method not allowed"
    exit 0
    ;;
esac
case $header in
  "" | --credentials | [Cc]ontent-[Tt]ype:*) echo allowed ;;
  *) echo "blocked: header not allowed" ;;
esac
EOF
chmod +x ~/bin/cors-audit
