# Wrong: the bytes are turned into GB of a thousand million bytes, not GiB.
# 7 billion parameters at 16 bits come out as 14.0 instead of 13.0, about
# 7% too much, and a card's memory, which nvidia-smi gives in MiB, would
# look fuller than it is.
sed -i -e 's|bytes_each = \.\.\.|bytes_each = bits / 8|' \
  -e 's|bytes_each \.\.\.|bytes_each / 1000000000|' \
  -e 's|needed = weights \.\.\.|needed = weights * (100 + headroom) / 100|' ~/bin/vram-fit
~/bin/vram-fit 7 16 16 25
