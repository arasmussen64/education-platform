# Wrong: the headroom is left out, so what is needed is the weights alone.
# 13.0 GiB of weights then "fit" a 16 GiB card, and the program runs out of
# card memory as soon as its inputs and working space arrive.
sed -i -e 's|bytes_each = \.\.\.|bytes_each = bits / 8|' \
  -e 's|bytes_each \.\.\.|bytes_each / 1073741824|' \
  -e 's|needed = weights \.\.\.|needed = weights|' ~/bin/vram-fit
~/bin/vram-fit 7 16 16 25
