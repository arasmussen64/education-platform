# Wrong: the network is the address itself, with its host bits never
# cleared, so the "block" starts wherever the address is. Right only when
# the address happens to be its block's first.
sed -i \
  -e 's#^mask=\$(( \.\.\. ))#mask=$(( (0xFFFFFFFF << (32 - prefix)) \& 0xFFFFFFFF ))#' \
  -e 's#^network=\$(( n \.\.\. mask ))#network=$(( n ))#' \
  -e 's#^last=\$(( \.\.\. ))#last=$(( network | wildcard ))#' \
  -e 's#aws | azure) kept=\.\.\.; first=\.\.\. ;;#aws | azure) kept=5; first=4 ;;#' \
  -e 's#google) kept=\.\.\.; first=\.\.\. ;;#google) kept=4; first=2 ;;#' \
  ~/bin/cidr-info
