uname -m; dpkg --print-architecture
gcc -O2 -o ~/hello ~/src/hello.c && file ~/hello && ~/hello
aarch64-linux-gnu-gcc -O2 -static -o ~/hello-arm64 ~/src/hello.c && file ~/hello-arm64
~/hello-arm64; echo "exit status $?"
qemu-aarch64-static ~/hello-arm64
gcc -O2 -o ~/count ~/src/count.c && aarch64-linux-gnu-gcc -O2 -static -o ~/count-arm64 ~/src/count.c && ~/count && qemu-aarch64-static ~/count-arm64
unzip -l ~/lib/crc.jar && unzip -p ~/lib/crc.jar native/libcrc.so | file -b -
mkdir -p ~/example
uname -m > ~/example/arch.txt
file -b ~/hello | awk -F', ' '{print $2}' >> ~/example/arch.txt
file -b ~/hello-arm64 | awk -F', ' '{print $2}' >> ~/example/arch.txt
unzip -p ~/lib/crc.jar native/libcrc.so | file -b - | awk -F', ' '{print $2}' >> ~/example/arch.txt
cat ~/example/arch.txt
