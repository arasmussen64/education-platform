# Wrong: the mask shifts by 33 - prefix, one place too far, so it has one
# 1 bit too few: every block comes out twice its real size.
sed -i \
  -e 's#^mask=\$(( \.\.\. ))#mask=$(( (0xFFFFFFFF << (33 - prefix)) \& 0xFFFFFFFF ))#' \
  -e 's#^network=\$(( n \.\.\. mask ))#network=$(( n \& mask ))#' \
  -e 's#^last=\$(( \.\.\. ))#last=$(( network | wildcard ))#' \
  -e 's#aws | azure) kept=\.\.\.; first=\.\.\. ;;#aws | azure) kept=5; first=4 ;;#' \
  -e 's#google) kept=\.\.\.; first=\.\.\. ;;#google) kept=4; first=2 ;;#' \
  ~/bin/cidr-info
