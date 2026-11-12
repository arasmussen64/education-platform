#!/bin/bash
# v6-subnet PREFIX48 R Z T -> short form of PREFIX:RZTT::/64 by the simplified rule:
# strip leading zeros per group, then replace the trailing run of zero groups with ::
p=${1%/*}; p=${p%::}; IFS=: read -r g1 g2 g3 <<< "$p"
groups=("$g1" "${g2:-0}" "${g3:-0}" "$(printf '%x%x%02x' "$2" "$3" "$4")" 0 0 0 0)
out=(); for g in "${groups[@]}"; do out+=("$(printf '%x' "0x$g")"); done
n=8; while (( n > 0 )) && [ "${out[n-1]}" = 0 ]; do n=$((n - 1)); done
s=$(IFS=:; echo "${out[*]:0:n}"); echo "${s}::/64"
