/* hello: says which kind of machine it is running on. */
#include <stdio.h>
#include <sys/utsname.h>

int main(void) {
    struct utsname machine;
    uname(&machine);
    printf("hello from %s\n", machine.machine);
    return 0;
}
