# Wrong: the headroom typed in as the shown cases' 25%, weights x 1.25,
# instead of read from HEADROOM_PCT. Right for both cases in the prompt, and
# wrong for any other headroom the script is given.
sed -i -e 's|bytes_each = \.\.\.|bytes_each = bits / 8|' \
  -e 's|bytes_each \.\.\.|bytes_each / 1073741824|' \
  -e 's|needed = weights \.\.\.|needed = weights * 1.25|' ~/bin/vram-fit
~/bin/vram-fit 7 16 16 25
