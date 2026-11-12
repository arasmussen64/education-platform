ip2int() { local a b c d; IFS=. read -r a b c d <<< "$1"; echo $(( (a << 24) | (b << 16) | (c << 8) | d )); }
int2ip() { echo "$(( $1 >> 24 & 255 )).$(( $1 >> 16 & 255 )).$(( $1 >> 8 & 255 )).$(( $1 & 255 ))"; }
mask() { echo $(( (0xFFFFFFFF << (32 - $1)) & 0xFFFFFFFF )); }
n=$(ip2int 10.20.30.77); m=$(mask 27)
echo "int=$n mask=$(int2ip $m) net=$(int2ip $(( n & m ))) last=$(int2ip $(( n | (~m & 0xFFFFFFFF) )))"
overlap() { local a=${1%/*} p=${1#*/} b=${2%/*} q=${2#*/}; local k=$(( p < q ? p : q )); local x y; x=$(ip2int $a); y=$(ip2int $b); [ $(( x >> (32 - k) )) -eq $(( y >> (32 - k) )) ] && echo yes || echo no; }
for pair in "10.0.0.0/8 10.200.0.0/16" "10.0.0.0/25 10.0.0.128/25" "172.16.0.0/12 172.32.0.0/16" "0.0.0.0/0 192.168.1.0/24" "192.168.1.5/32 192.168.1.0/30"; do echo "$pair -> $(overlap $pair)"; done
echo "bash ${BASH_VERSION}"
printf 'awk test: '; echo 4294967295 | awk '{printf "%d %.0f %s\n", $1, $1, $1 + 0; print int($1 / 16777216) % 256}'
echo 3232235777 | awk '{n=$1; printf "%d.%d.%d.%d\n", int(n/16777216)%256, int(n/65536)%256, int(n/256)%256, n%256}'
