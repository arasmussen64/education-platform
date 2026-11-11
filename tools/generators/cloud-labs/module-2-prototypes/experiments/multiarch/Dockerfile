# The simple way: everything, including the compiler, runs as the target
# architecture. For linux/arm64 on an x86 machine that means under QEMU.
FROM ubuntu:24.04 AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*
COPY hello.c /src/hello.c
RUN gcc -O2 -static -o /hello /src/hello.c
FROM scratch
COPY --from=build /hello /hello
CMD ["/hello"]
