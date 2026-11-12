# Wrong: AWS and Azure keep back five addresses, but the first usable one
# is taken as the classic one, straight after the network address. Both
# keep the first four, so a machine's first address is the fifth.
sed -i \
  -e 's#^mask=\$(( \.\.\. ))#mask=$(( (0xFFFFFFFF << (32 - prefix)) \& 0xFFFFFFFF ))#' \
  -e 's#^network=\$(( n \.\.\. mask ))#network=$(( n \& mask ))#' \
  -e 's#^last=\$(( \.\.\. ))#last=$(( network | wildcard ))#' \
  -e 's#aws | azure) kept=\.\.\.; first=\.\.\. ;;#aws | azure) kept=5; first=1 ;;#' \
  -e 's#google) kept=\.\.\.; first=\.\.\. ;;#google) kept=4; first=2 ;;#' \
  ~/bin/cidr-info
