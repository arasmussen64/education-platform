# Wrong: the internet and the card readers are fixed and saved, but r3
# still sends the office's traffic over the emergency link, so the stock
# app's replies never pass r2 and the app still times out.
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory' > /dev/null
