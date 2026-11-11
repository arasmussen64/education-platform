/* count: counts to 200 million and says how long it took. */
#include <stdio.h>
#include <time.h>

int main(void) {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    volatile unsigned long total = 0;
    for (unsigned long i = 0; i < 200000000UL; i++) {
        total += i % 7;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    double seconds = (double)(end.tv_sec - start.tv_sec)
        + (double)(end.tv_nsec - start.tv_nsec) / 1e9;
    printf("counted to 200000000 in %.2f seconds\n", seconds);
    return 0;
}
