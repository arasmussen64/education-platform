# Wrong: the earnings leave out the vCPUs. A t3.small earns its baseline on
# each of its two vCPUs, 0.4 credits a minute, not 0.2.
sed -i -e 's|earned = \.\.\.|earned = baseline / 100|' \
  -e 's|spent = \.\.\.|spent = vcpus * $2 / 100|' \
  -e 's|^    \.\.\. .*|    if (b < 0) b = 0; if (b > max) b = max|' ~/bin/credit-bucket
~/bin/credit-bucket /srv/burst/shop-web
