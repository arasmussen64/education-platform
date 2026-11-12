#!/bin/bash
# The lab's story, at every boot: web3 was taken out of rotation by hand,
# through the balancer's runtime API, as the on-call engineer does after
# every restart of the balancer.
for i in $(seq 1 40); do
  if echo "show info" | on lb socat -t 2 stdio /run/haproxy/admin.sock 2> /dev/null | grep '^Pid:' > /dev/null; then
    echo "set server web/web3 state maint" | on lb socat -t 2 stdio /run/haproxy/admin.sock > /dev/null
    exit 0
  fi
  sleep 0.5
done
exit 0
