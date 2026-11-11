#!/bin/bash
# Reliability probe: N lab containers started at once (CI runs four labs at a
# time), each booted, joined with the reference solution and logged in to.
# Prints one line per container. Removes everything it starts.
# Usage: parallel_boot.sh N ROUNDS SOLUTION_FILE
export MSYS_NO_PATHCONV=1
N=${1:-4}; ROUNDS=${2:-2}; SOLUTION=$3
IMG=lab-csa.hw.windows-ad-build-join-the-domain:r1
SSH="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 -o LogLevel=ERROR -o ConnectTimeout=5"

one() {
  local name=$1 start=$(date +%s)
  docker run -d --name "$name" --hostname lab --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock "$IMG" /sbin/init > /dev/null
  local state=unknown
  for _ in $(seq 1 480); do
    state=$(docker exec "$name" systemctl is-system-running 2>/dev/null)
    [ "$state" = running ] || [ "$state" = degraded ] && break
    sleep 0.5
  done
  local booted=$(( $(date +%s) - start ))
  docker cp "$SOLUTION" "$name:/tmp/apply.sh" > /dev/null
  docker exec -u learner -w /home/learner "$name" bash /tmp/apply.sh > /dev/null 2>&1
  local applied=$(( $(date +%s) - start ))
  local who
  who=$(docker exec "$name" bash -c "sshpass -p 'Alice-Pass-1' ssh $SSH -l alice@ad.shop.test 127.0.0.1 whoami" 2>&1 | tail -n 1)
  local bob
  bob=$(docker exec "$name" bash -c "sshpass -p 'Bob-Pass-1' ssh $SSH -l bob@ad.shop.test 127.0.0.1 whoami > /dev/null 2>&1 && echo bob-in || echo bob-out")
  local done_at=$(( $(date +%s) - start ))
  echo "$name: state=$state booted=${booted}s joined=${applied}s checked=${done_at}s alice=[$who] $bob"
  docker rm -f "$name" > /dev/null
}

for round in $(seq 1 "$ROUNDS"); do
  for i in $(seq 1 "$N"); do one "m2ad-par-$round-$i" & done
  wait
done
