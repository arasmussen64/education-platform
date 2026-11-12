# Wrong: the last address is one past the block (the network plus the
# whole block's size), which is the first address of the next block.
sed -i \
  -e 's#^mask=\$(( \.\.\. ))#mask=$(( (0xFFFFFFFF << (32 - prefix)) \& 0xFFFFFFFF ))#' \
  -e 's#^network=\$(( n \.\.\. mask ))#network=$(( n \& mask ))#' \
  -e 's#^last=\$(( \.\.\. ))#last=$(( (network | wildcard) + 1 ))#' \
  -e 's#aws | azure) kept=\.\.\.; first=\.\.\. ;;#aws | azure) kept=5; first=4 ;;#' \
  -e 's#google) kept=\.\.\.; first=\.\.\. ;;#google) kept=4; first=2 ;;#' \
  ~/bin/cidr-info
