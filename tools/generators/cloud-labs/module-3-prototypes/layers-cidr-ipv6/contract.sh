#!/bin/bash
# contract.sh IMAGE LABDIR: pristine, solution, each wrong fix, each in a fresh container.
export MSYS_NO_PATHCONV=1
img=$1; dir=$2
run() { # name script
  c=l1proto-ct-$$; docker rm -f $c >/dev/null 2>&1
  t0=$(date +%s)
  docker run -d --name $c --hostname lab --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock $img /sbin/init >/dev/null
  for i in $(seq 1 60); do s=$(docker exec $c systemctl is-system-running 2>/dev/null); case $s in running|degraded) break;; esac; sleep 1; done
  t1=$(date +%s)
  [ -n "$2" ] && docker exec -i -u learner -w /home/learner $c bash < "$2" > /dev/null 2>&1
  docker cp "$dir/checks.sh" $c:/root/checks.sh >/dev/null
  t2=$(date +%s); res=$(docker exec $c bash /root/checks.sh); t3=$(date +%s)
  echo "== $1 (boot $((t1-t0))s, fix $((t2-t1))s, checks $((t3-t2))s, state $s)"; echo "$res" | sed 's/^/   /'
  if [ "$1" = solution ] && [ -n "$RESTART" ]; then docker restart $c >/dev/null; sleep 8; echo "   -- after docker restart:"; docker exec $c bash /root/checks.sh | sed 's/^/   /'; fi
  docker rm -f $c >/dev/null
}
run pristine ""
RESTART=1 run solution "$dir/solution.sh"
for w in "$dir"/wrong/*.sh; do run "wrong/$(basename $w .sh)" "$w"; done
