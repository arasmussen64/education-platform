# Wrong: the balance may go below 0. A bucket can't hold less than nothing,
# so the minutes held to the baseline and the final balance come out wrong.
sed -i -e 's|earned = \.\.\.|earned = vcpus * baseline / 100|' \
  -e 's|spent = \.\.\.|spent = vcpus * $2 / 100|' \
  -e 's|^    \.\.\. .*|    if (b > max) b = max|' ~/bin/credit-bucket
~/bin/credit-bucket /srv/burst/shop-web
