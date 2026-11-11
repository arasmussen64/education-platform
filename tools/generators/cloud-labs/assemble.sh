#!/bin/bash
# Assembles every systemd lab's Dockerfile from the shared head and the
# lab's tail (and copies the files a topic's labs share), so a change to
# the head reaches them all. Reads the folders beside this script.
set -euo pipefail
S=$(cd "$(dirname "$0")" && pwd)
T="${TOPICS_DIR:?set TOPICS_DIR to the folder to write into (a scratch copy of content/topics)}"
head="$S/services/Dockerfile.head"

assemble() { # topic tails-dir lab:tail...
  local topic="$1" tails="$2"; shift 2
  for pair in "$@"; do
    local lab="${pair%%:*}" tail="${pair#*:}" dir="$T/$topic/exercises/${pair%%:*}"
    { cat "$head"; [ -f "$S/$tails/tail-common" ] && cat "$S/$tails/tail-common"; cat "$S/$tails/tail-$tail"; } > "$dir/Dockerfile"
  done
}

assemble csa.linux.services services example-first-service:example fill-unit-gaps:fill write-unit:write build-restarting-api:build debug-service-wont-start:debug
assemble csa.linux.processes processes example-stop-a-runaway:example fill-run-report:fill write-graceful-stop:write build-nightly-runner:build debug-stop-workers:debug
assemble csa.linux.permissions permissions example-read-and-set-modes:example fill-service-account:fill write-share-folder:write build-lock-down-the-server:build debug-cant-log-in:debug
assemble csa.linux.packages packages example-update-then-look:example fill-patch-server:fill write-security-updates:write build-patch-day:build debug-nightly-patch:debug
assemble csa.linux.storage storage example-new-disk:example fill-add-disk:fill write-disk-report:write build-full-disk:build debug-wont-mount:debug

# Files every storage lab's image needs beside its Dockerfile.
for lab in example-new-disk fill-add-disk write-disk-report build-full-disk debug-wont-mount; do
  cp "$S/storage/disks.sh" "$S/storage/teardown.sh" "$S/storage/lab-disks.service" "$S/storage/lab-grow" "$T/csa.linux.storage/exercises/$lab/"
done
for lab in write-disk-report build-full-disk; do
  cp "$S/storage/log-shipper" "$S/storage/log-shipper.service" "$T/csa.linux.storage/exercises/$lab/"
done

assemble csa.linux.memory memory example-limit-a-hog:example fill-memory-report:fill write-limited-run:write build-contain-the-leak:build debug-oomkilled:debug
for lab in example-limit-a-hog fill-memory-report write-limited-run; do cp "$S/memory/memhog" "$T/csa.linux.memory/exercises/$lab/"; done
cp "$S/memory/leaky" "$T/csa.linux.memory/exercises/build-contain-the-leak/"
cp "$S/memory/leaky" "$S/memory/shop-cache" "$T/csa.linux.memory/exercises/debug-oomkilled/"

assemble csa.linux.cpu cpu example-quota-a-spinner:example fill-cpu-report:fill write-cpu-cap:write build-share-the-cpu:build debug-throttled-api:debug
for lab in example-quota-a-spinner fill-cpu-report write-cpu-cap build-share-the-cpu debug-throttled-api; do cp "$S/cpu/spin" "$T/csa.linux.cpu/exercises/$lab/"; done

assemble csa.linux.containers containers example-container-by-hand:example fill-run-in-box:fill write-layers:write build-box:build debug-leaky-box:debug
for lab in example-container-by-hand fill-run-in-box write-layers build-box debug-leaky-box; do cp "$S/containers/make-rootfs.sh" "$S/containers/rootfs-devices.sh" "$S/containers/box-rootfs.service" "$T/csa.linux.containers/exercises/$lab/"; done
assemble csa.linux.net-tools net example-whats-listening:example fill-net-report:fill write-socket-report:write build-shop-firewall:build debug-not-from-the-office:debug
for lab in example-whats-listening fill-net-report write-socket-report build-shop-firewall debug-not-from-the-office; do
  cp "$S/net/network.sh" "$S/net/lab-network.service" "$S/net/office-resolv.conf" "$S/net/shop.conf" "$S/net/dnsmasq-lab.conf" "$S/net/from-office" "$S/net/shop-api" "$S/net/shop-api.service" "$S/net/shop-db" "$S/net/shop-db.service" "$S/net/office-monitor" "$S/net/office-monitor.service" "$T/csa.linux.net-tools/exercises/$lab/"
done
cp "$S/net/shop-cache" "$S/net/shop-cache.service" "$S/net/shop-cache-warm" "$S/net/shop-cache-warm.service" "$T/csa.linux.net-tools/exercises/write-socket-report/"
assemble csa.linux.boot boot example-first-boot:example fill-user-data:fill write-imds-get:write build-close-the-hole:build debug-wont-come-up:debug
for lab in example-first-boot fill-user-data write-imds-get build-close-the-hole debug-wont-come-up; do
  cp "$S/boot/make-repo.sh" "$S/boot/cloud.sh" "$S/boot/lab-imds" "$S/boot/lab-launch" "$S/boot/lab-reboot" "$S/boot/lab-imds-options" "$S/boot/lab-cloud.service" "$S/boot/lab-imds.service" "$S/boot/90_lab.cfg" "$S/boot/ds-identify.cfg" "$S/boot/meta-data" "$T/csa.linux.boot/exercises/$lab/"
done
cp "$S/boot/user-data-example" "$T/csa.linux.boot/exercises/example-first-boot/"
cp "$S/boot/user-data-fill.starter" "$T/csa.linux.boot/exercises/fill-user-data/"
cp "$S/boot/region-tag" "$T/csa.linux.boot/exercises/build-close-the-hole/"
cp "$S/boot/user-data-debug.broken" "$T/csa.linux.boot/exercises/debug-wont-come-up/"
assemble csa.linux.triage triage example-sixty-seconds:example fill-triage-report:fill write-cpu-culprit:write build-busiest-service:build debug-syscall-storm:debug
cp "$S/triage/spin" "$S/triage/shop-worker.service" "$S/triage/shop-logger" "$S/triage/shop-logger.service" "$T/csa.linux.triage/exercises/example-sixty-seconds/"
cp "$S/triage/spin" "$S/triage/shop-worker.service" "$T/csa.linux.triage/exercises/fill-triage-report/"
cp "$S/triage/triage-report.starter" "$T/csa.linux.triage/exercises/fill-triage-report/"
cp "$S/triage/spin" "$S/triage/shop-worker.service" "$T/csa.linux.triage/exercises/write-cpu-culprit/"
cp "$S/triage/spin" "$S/triage/shop-worker.service" "$S/triage/shop-api-idle.service" "$S/triage/shop-db-idle.service" "$T/csa.linux.triage/exercises/build-busiest-service/"
cp "$S/triage/shop-tailer" "$S/triage/shop-tailer.service" "$S/triage/shop-api-idle.service" "$T/csa.linux.triage/exercises/debug-syscall-storm/"
assemble csa.linux.hardening hardening example-harden-ssh:example fill-sshd-hardening:fill write-exposed-ports:write build-harden-the-server:build debug-locked-out:debug
cp "$S/hardening/shop-debug" "$S/hardening/shop-debug.service" "$T/csa.linux.hardening/exercises/example-harden-ssh/"
cp "$S/hardening/sshd-hardening.starter" "$T/csa.linux.hardening/exercises/fill-sshd-hardening/"
cp "$S/hardening/shop-debug" "$S/hardening/shop-debug.service" "$S/hardening/shop-db" "$S/hardening/shop-db.service" "$T/csa.linux.hardening/exercises/write-exposed-ports/"
cp "$S/hardening/shop-debug" "$S/hardening/shop-debug.service" "$T/csa.linux.hardening/exercises/build-harden-the-server/"
cp "$S/hardening/sshd-broken.conf" "$T/csa.linux.hardening/exercises/debug-locked-out/"
assemble csa.m1.checkpoint checkpoint build-stand-up-server:standup-shop debug-broken-server:broken example-stand-up-blog:standup-blog step-run-the-service:step-service step-put-up-the-firewall:step-firewall step-harden-ssh:step-ssh step-the-whole-runbook:standup-shop build-stand-up-gateway:standup-gateway build-stand-up-ledger:standup-ledger
cp "$S/checkpoint/shop-api" "$S/checkpoint/shop-api.service" "$T/csa.m1.checkpoint/exercises/build-stand-up-server/"
cp "$S/checkpoint/shop-api" "$S/checkpoint/spin" "$S/checkpoint/shop-api-broken.service" "$S/checkpoint/shop-worker.service" "$S/checkpoint/lab-disk.sh" "$S/checkpoint/lab-disk.service" "$S/checkpoint/nftables-22only.conf" "$T/csa.m1.checkpoint/exercises/debug-broken-server/"
cp "$S/checkpoint/webapp" "$S/checkpoint/blog-web.service" "$T/csa.m1.checkpoint/exercises/example-stand-up-blog/"
cp "$S/checkpoint/shop-api" "$S/checkpoint/shop-api.service" "$S/checkpoint/nftables-shop.conf" "$S/checkpoint/90-hardening.conf" "$T/csa.m1.checkpoint/exercises/step-run-the-service/"
cp "$S/checkpoint/shop-api" "$S/checkpoint/shop-api.service" "$S/checkpoint/90-hardening.conf" "$T/csa.m1.checkpoint/exercises/step-put-up-the-firewall/"
cp "$S/checkpoint/shop-api" "$S/checkpoint/shop-api.service" "$S/checkpoint/nftables-shop.conf" "$T/csa.m1.checkpoint/exercises/step-harden-ssh/"
cp "$S/checkpoint/shop-api" "$S/checkpoint/shop-api.service" "$T/csa.m1.checkpoint/exercises/step-the-whole-runbook/"
cp "$S/checkpoint/webapp" "$S/checkpoint/gateway.service" "$T/csa.m1.checkpoint/exercises/build-stand-up-gateway/"
cp "$S/checkpoint/webapp" "$S/checkpoint/ledger.service" "$T/csa.m1.checkpoint/exercises/build-stand-up-ledger/"
echo "assembled"
