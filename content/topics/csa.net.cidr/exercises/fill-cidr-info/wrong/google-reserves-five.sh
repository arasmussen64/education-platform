# Wrong: Google is given AWS's and Azure's rule, five kept back and the
# first usable address fourth from the start. Google keeps four: the first
# two and the last two.
sed -i \
  -e 's#^mask=\$(( \.\.\. ))#mask=$(( (0xFFFFFFFF << (32 - prefix)) \& 0xFFFFFFFF ))#' \
  -e 's#^network=\$(( n \.\.\. mask ))#network=$(( n \& mask ))#' \
  -e 's#^last=\$(( \.\.\. ))#last=$(( network | wildcard ))#' \
  -e 's#aws | azure) kept=\.\.\.; first=\.\.\. ;;#aws | azure) kept=5; first=4 ;;#' \
  -e 's#google) kept=\.\.\.; first=\.\.\. ;;#google) kept=5; first=4 ;;#' \
  ~/bin/cidr-info
