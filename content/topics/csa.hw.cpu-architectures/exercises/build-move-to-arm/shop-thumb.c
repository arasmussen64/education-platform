/* shop-thumb: evens out a thumbnail's brightness. With --selftest it runs on
   a test picture and prints a checksum of the result. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define PIXELS 65536

static uint8_t picture[PIXELS];
static uint8_t result[PIXELS];

/* The inner loop: every pixel brightened the same way. A compiler can do
   many pixels at once here with vector instructions. */
static void brighten(uint8_t *out, const uint8_t *in, int count) {
    for (int i = 0; i < count; i++) {
        out[i] = (uint8_t)((in[i] * 3u) / 4u + 32u);
    }
}

int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "--selftest") != 0) {
        fprintf(stderr, "usage: shop-thumb --selftest\n");
        return 2;
    }
    for (int i = 0; i < PIXELS; i++) {
        picture[i] = (uint8_t)(i * 31 + 7);
    }
    brighten(result, picture, PIXELS);
    uint32_t sum = 0;
    for (int i = 0; i < PIXELS; i++) {
        sum = sum * 31u + result[i];
    }
    printf("shop-thumb selftest: %d pixels, checksum %08x\n", PIXELS, (unsigned)sum);
    return 0;
}
