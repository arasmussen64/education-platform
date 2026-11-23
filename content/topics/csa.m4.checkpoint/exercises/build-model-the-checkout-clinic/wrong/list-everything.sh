#!/bin/bash
# WRONG: a model that lists everything everywhere and reads nothing of the
# design's facts. It draws and scopes the design as the solution does, then
# writes a threat under every letter of every flow, at the ratings and with
# the two controls that suit each letter somewhere in this story, and two
# techniques on every threat. It keeps every per-threat cap and chooses
# nothing.
cat > ~/model.tm <<'EOF'
zone internet  anyone on the internet
zone provider  PayHub, the payment provider
zone cloud     the clinic's cloud network
zone office    the office network at reception

element patient      external internet  a patient's browser
element psp          external provider  PayHub's hosted payment page and API
element portal       process  cloud     the patient portal
element billing      process  cloud     invoices and their emailed links
element invoices-db  store    cloud     the invoices
element terminal     process  office    the card terminal at reception
element reception-pc process  office    the reception desk's PCs

flow f1 patient      portal      book, and start a payment
flow f2 patient      psp         pay on PayHub's hosted page
flow f3 psp          portal      PayHub sends the browser back with the result
flow f4 portal       billing     look an invoice up and mark it paid
flow f5 patient      billing     open an invoice from its emailed link
flow f6 billing      invoices-db read and write invoices
flow f7 terminal     psp         a card payment at reception
flow f8 reception-pc terminal    start a payment, and the admin page

scope portal       impacting it decides where patients are sent to type their card
scope billing      out no card data reaches it and the office network can't reach it
scope invoices-db  out it holds invoices only, in the cloud, apart from the terminal
scope terminal     cde card numbers pass through it on their way to PayHub
scope reception-pc cde it shares the terminal's office network with nothing filtering
EOF
declare -A rate=([I]="2:3 3:2" [S]="3:2 2:3" [T]="1:1" [E]="1:3" [D]="1:1" [R]="1:1")
declare -A kinds=([I]="authz patch" [S]="signing mfa" [T]="signing" [E]="authz" [D]="rate-limit" [R]="audit-log")
n=0 nines="" sixes=""
for f in f1 f2 f3 f4 f5 f6 f7 f8; do
  for letter in I S T E D R; do
    for r in ${rate[$letter]}; do
      n=$((n + 1)) L=${r%:*} I=${r#*:}
      echo "threat x$n $f $letter $L $I $((L * I)) An attacker number $n can do harm number $n"
      k=0
      for kind in ${kinds[$letter]}; do
        k=$((k + 1))
        echo "control c$n-$k x$n $kind control number $k for threat $n"
      done
      echo "attack x$n T1190"
      echo "attack x$n T1078"
      if [ $((L * I)) -eq 9 ]; then nines="$nines x$n"; fi
      if [ $((L * I)) -eq 6 ]; then sixes="$sixes x$n"; fi
    done
  done
done >> ~/model.tm
first="$nines $sixes"
first=${first#"${first%%[! ]*}"}
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
