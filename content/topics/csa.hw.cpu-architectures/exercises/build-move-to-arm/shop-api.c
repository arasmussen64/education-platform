/* shop-api: answers the shop's web requests. With --selftest it routes a
   few test requests and prints what it found. */
#include <stdio.h>
#include <string.h>

static const char *routes[] = {"/basket", "/checkout", "/orders"};

static int route(const char *path) {
    for (int i = 0; i < 3; i++) {
        if (strcmp(path, routes[i]) == 0) {
            return i;
        }
    }
    return -1;
}

int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "--selftest") != 0) {
        fprintf(stderr, "usage: shop-api --selftest\n");
        return 2;
    }
    const char *tests[] = {"/orders", "/basket", "/missing", "/checkout"};
    int found = 0;
    unsigned score = 0;
    for (int i = 0; i < 4; i++) {
        int r = route(tests[i]);
        if (r >= 0) {
            found++;
            score = score * 7u + (unsigned)r + 1u;
        }
    }
    printf("shop-api selftest: %d of 4 routes found, score %u\n", found, score);
    return 0;
}
