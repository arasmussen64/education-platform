# Wrong: the right program, built by hand and put in bin/, while the recipe
# is left as it was. The next release, built by the recipe, brings all
# three faults back.
aarch64-linux-gnu-gcc -O2 -static -o /srv/release/bin/shop-resize /srv/release/src/shop-resize.c
