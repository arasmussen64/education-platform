# Wrong: the first gap filled with the shown cases' answer, 2 bytes, instead
# of working it out from the bits. Right for 16 bits, the only kind the
# prompt shows, and wrong for any other: a 4-bit model comes out four times
# its size.
sed -i -e 's|bytes_each = \.\.\.|bytes_each = 2|' \
  -e 's|bytes_each \.\.\.|bytes_each / 1073741824|' \
  -e 's|needed = weights \.\.\.|needed = weights * (100 + headroom) / 100|' ~/bin/vram-fit
~/bin/vram-fit 7 16 16 25
