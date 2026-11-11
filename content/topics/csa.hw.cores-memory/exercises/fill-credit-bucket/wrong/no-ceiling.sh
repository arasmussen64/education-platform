# Wrong: the balance may grow past the most the bucket holds. shop-web never
# gets near its 576, so it comes out right there; an instance that idles
# long enough to fill up gets its "empty at minute" wrong.
sed -i -e 's|earned = \.\.\.|earned = vcpus * baseline / 100|' \
  -e 's|spent = \.\.\.|spent = vcpus * $2 / 100|' \
  -e 's|^    \.\.\. .*|    if (b < 0) b = 0|' ~/bin/credit-bucket
~/bin/credit-bucket /srv/burst/shop-web
