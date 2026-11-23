#!/bin/bash
# WRONG: a model that lists everything everywhere and reads nothing of the
# design's facts. It draws the design as the solution does, then writes
# three threats under every letter of every flow that crosses a boundary,
# at three ratings, each with the same two controls for its letter, two
# techniques, and an abuse case for every risk of 6 or more. It keeps every
# per-flow and per-threat cap and chooses nothing: 70 threats, 35 of them
# rated 6 or more. The whole-model cap turns it away.
cat > ~/model.tm <<'EOF'
zone internet anyone on the internet
zone clinic the clinic's own cloud network
zone sms-co the SMS company
zone cloud-storage the cloud provider's storage service
element patient external internet a patient's browser or phone
element staff external internet a member of staff's laptop or phone
element analyst external internet the accounting firm's analyst
element web process clinic the booking site and its staff pages
element bookings-db store clinic patients, phone numbers and appointments
element sms-gateway external sms-co the SMS company's servers
element exports store cloud-storage the bucket of nightly export files
flow f1 patient web book, change or cancel an appointment
flow f2 staff web sign in and change bookings
flow f3 web bookings-db read and write bookings
flow f4 sms-gateway web delivery and reply reports to /hooks/sms
flow f5 web exports write the nightly export file
flow f6 analyst exports download an export file
EOF
declare -A rate=([S]="3:3 3:2 2:3" [T]="3:3 3:2 1:1" [R]="2:2 1:1 1:2" [I]="3:3 2:3 1:1" [D]="1:1" [E]="1:1")
declare -A kinds=([S]="mfa signing" [T]="signing integrity" [R]="audit-log signing" [I]="authz encryption" [D]="rate-limit" [E]="authz")
n=0 nines="" sixes=""
for f in f1 f2 f4 f5 f6; do
  for letter in S T R I D E; do
    for r in ${rate[$letter]}; do
      n=$((n + 1)) L=${r%:*} I=${r#*:}
      echo "threat x$n $f $letter $L $I $((L * I)) An attacker number $n can do harm number $n"
      k=0
      for kind in ${kinds[$letter]}; do
        k=$((k + 1))
        echo "control c$n-$k x$n $kind control number $k for threat $n"
      done
      echo "attack x$n T1078"
      echo "attack x$n T1530"
      if [ $((L * I)) -ge 6 ]; then
        echo "abuse a$n x$n As an attacker, I do harm number $n so that I gain number $n"
        echo "test t$n a$n try harm number $n and expect a refusal"
      fi
      if [ $((L * I)) -eq 9 ]; then nines="$nines x$n"; fi
      if [ $((L * I)) -eq 6 ]; then sixes="$sixes x$n"; fi
    done
  done
done >> ~/model.tm
first=${nines# }
first=${first%% *}
cat >> ~/model.tm <<EOF
top$nines$sixes
goal g1 $first reach the goal
node n1 g1 or one way or another
node n2 n1 and two steps
leaf l1 n2 10 step one
leaf l2 n2 10 step two
leaf l3 n1 5 the other way
cheapest g1 5
EOF
