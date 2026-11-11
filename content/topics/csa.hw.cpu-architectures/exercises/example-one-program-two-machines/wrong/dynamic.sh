# Wrong: the Arm program is built without -static, so it expects to load
# the Arm C library from the machine it runs on. The emulator looks for
# /lib/ld-linux-aarch64.so.1, which an x86-64 machine doesn't have.
gcc -O2 -o ~/hello ~/src/hello.c
aarch64-linux-gnu-gcc -O2 -o ~/hello-arm64 ~/src/hello.c
gcc -O2 -o ~/count ~/src/count.c
aarch64-linux-gnu-gcc -O2 -static -o ~/count-arm64 ~/src/count.c
mkdir -p ~/example
uname -m > ~/example/arch.txt
file -b ~/hello | awk -F', ' '{print $2}' >> ~/example/arch.txt
file -b ~/hello-arm64 | awk -F', ' '{print $2}' >> ~/example/arch.txt
unzip -p ~/lib/crc.jar native/libcrc.so | file -b - | awk -F', ' '{print $2}' >> ~/example/arch.txt
