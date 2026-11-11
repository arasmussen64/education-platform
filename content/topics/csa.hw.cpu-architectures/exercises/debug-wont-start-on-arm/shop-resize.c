/* shop-resize: shrinks a product photo to half its width, averaging each
   pair of pixels, then deepens its shadows. With --selftest it runs on a
   test photo and prints a checksum of the result. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define WIDE 131072
#define NARROW (WIDE / 2)

static uint8_t photo[WIDE];
static uint8_t half[NARROW];
static uint8_t shaded[NARROW];

static void shrink(uint8_t *out, const uint8_t *in, int count) {
    for (int i = 0; i < count; i++) {
        out[i] = (uint8_t)((in[2 * i] + in[2 * i + 1] + 1u) / 2u);
    }
}

/* Every pixel darkened by its own brightness: a compiler can do many at
   once here with vector instructions. */
static void shade(uint8_t *out, const uint8_t *in, int count) {
    for (int i = 0; i < count; i++) {
        out[i] = (uint8_t)((in[i] * (unsigned)in[i]) / 255u);
    }
}

int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "--selftest") != 0) {
        fprintf(stderr, "usage: shop-resize --selftest\n");
        return 2;
    }
    for (int i = 0; i < WIDE; i++) {
        photo[i] = (uint8_t)(i * 17 + 3);
    }
    shrink(half, photo, NARROW);
    shade(shaded, half, NARROW);
    uint32_t sum = 0;
    for (int i = 0; i < NARROW; i++) {
        sum = sum * 33u + shaded[i];
    }
    printf("shop-resize selftest: %d pixels, checksum %08x\n", NARROW, (unsigned)sum);
    return 0;
}
