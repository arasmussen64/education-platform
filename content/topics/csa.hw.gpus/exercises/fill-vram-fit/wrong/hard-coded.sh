# Wrong: the gaps are gone, but the script prints the answers to the two
# cases the prompt shows, whatever it is given. It never works anything out.
cat > ~/bin/vram-fit <<'EOF'
#!/bin/bash
if [ $# -ne 4 ]; then
  echo "Usage: vram-fit PARAMS_BILLION BITS CARD_GIB HEADROOM_PCT" >&2
  exit 2
fi
echo "weights: 13.0 GiB"
echo "needed: 16.3 GiB"
if [ "$3" -ge 22 ]; then echo "fits: yes"; else echo "fits: no"; fi
EOF
~/bin/vram-fit 7 16 16 25
