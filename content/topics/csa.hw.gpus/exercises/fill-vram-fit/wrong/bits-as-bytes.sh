# Wrong: the bits are taken for bytes. A 16-bit parameter is 2 bytes, not
# 16, so every model comes out eight times its size.
sed -i -e 's|bytes_each = \.\.\.|bytes_each = bits|' \
  -e 's|bytes_each \.\.\.|bytes_each / 1073741824|' \
  -e 's|needed = weights \.\.\.|needed = weights * (100 + headroom) / 100|' ~/bin/vram-fit
~/bin/vram-fit 7 16 16 25
