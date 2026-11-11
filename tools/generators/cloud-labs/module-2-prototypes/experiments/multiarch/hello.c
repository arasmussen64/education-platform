#include <stdio.h>
#include <sys/utsname.h>
int main(void) {
    struct utsname u;
    uname(&u);
    printf("hello from %s\n", u.machine);
    return 0;
}
