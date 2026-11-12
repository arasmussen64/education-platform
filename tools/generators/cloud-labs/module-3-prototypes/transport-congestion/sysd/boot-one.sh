#!/bin/bash
# boot-one.sh NAME: starts one prototype container the way labcheck starts a
# systemd lab, waits for boot, copies in the helper scripts.
export MSYS_NO_PATHCONV=1
name="$1"
here="$(dirname "$0")"
docker run -d --name "$name" --hostname lab --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock tcproto-sysd:1 /sbin/init > /dev/null
for i in $(seq 1 30); do
  s=$(docker exec "$name" systemctl is-system-running 2>/dev/null)
  case "$s" in running|degraded) break ;; esac
  sleep 1
done
for f in cc-variant.sh check-quiet.sh variants.sh; do docker cp "$here/$f" "$name:/usr/local/lib/$f" > /dev/null; done
echo "$name booted: $s"
