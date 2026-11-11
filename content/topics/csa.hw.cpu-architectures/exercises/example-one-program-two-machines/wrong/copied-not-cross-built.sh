# Wrong: the "Arm" program is the x86-64 one copied under another name. A
# new name changes nothing inside the file: it still holds x86-64 machine
# code, and the Arm emulator refuses it.
gcc -O2 -o ~/hello ~/src/hello.c
cp ~/hello ~/hello-arm64
gcc -O2 -o ~/count ~/src/count.c
aarch64-linux-gnu-gcc -O2 -static -o ~/count-arm64 ~/src/count.c
mkdir -p ~/example
uname -m > ~/example/arch.txt
file -b ~/hello | awk -F', ' '{print $2}' >> ~/example/arch.txt
file -b ~/hello-arm64 | awk -F', ' '{print $2}' >> ~/example/arch.txt
unzip -p ~/lib/crc.jar native/libcrc.so | file -b - | awk -F', ' '{print $2}' >> ~/example/arch.txt
