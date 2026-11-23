# Wrong: the scores sorted as text. As text 9.8 comes after 10.0, because
# 9 is more than 1.
sed -i \
  -e 's#score\[\.\.\.\] = \.\.\.; next#score[$1] = $2; next#' \
  -e 's#score\[\$1\] : \.\.\.#score[$1] : 0#' \
  -e 's#listed) ? \.\.\. : \.\.\.#listed) ? "yes" : "no"#' \
  -e '/| sort -t/ s#\.\.\.$#-k5,5r -k4,4r -k3,3r -k1,1#' \
  ~/bin/triage
