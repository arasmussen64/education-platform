#!/bin/bash
# WRONG: a model that lists everything everywhere and reads nothing of the
# design's facts. It draws and scopes the design as the solution does, then
# writes a threat under every letter of every flow, at the ratings and with
# the two controls that suit each letter somewhere in this story, and two
# techniques on every threat. It keeps every per-threat cap and chooses
# nothing.
cat > ~/model.tm <<'EOF'
zone internet  anyone on the internet
zone devs      the developers' laptops, at home
zone provider  CardWorks, the payment provider
zone cloud     the bakery's cloud subnet
zone kitchen   the kitchen network

element customer  external internet  a customer's browser
element developer external devs      a developer's laptop
element psp       external provider  CardWorks' payment API
element shopfront process  cloud     the bakery's pages and its card form
element orders    process  cloud     takes orders and charges cards
element cards-db  store    cloud     the saved card numbers
element bake-list store    kitchen   the kitchen's print server

flow f1 customer  shopfront browse, sign in, order and pay
flow f2 shopfront orders    the order with its card number
flow f3 orders    psp       charge the card
flow f4 orders    cards-db  save the card for repeat orders
flow f5 orders    bake-list the day's loaves and cakes
flow f6 developer cards-db  questions answered from the database

scope shopfront cde card numbers are typed into its form and pass through it
scope orders    cde it takes each card number and charges it
scope cards-db  cde it stores card numbers for repeat orders
scope bake-list out it is firewalled, gets loaf counts only and opens nothing back
EOF
declare -A rate=([E]="3:3" [I]="2:3" [T]="3:2" [R]="2:2" [S]="1:1" [D]="1:1")
declare -A kinds=([E]="authz least-privilege" [I]="tls encryption" [T]="input-validation" [R]="audit-log" [S]="mfa" [D]="rate-limit")
n=0 nines="" sixes=""
for f in f1 f2 f3 f4 f5 f6; do
  for letter in E I T R S D; do
    for r in ${rate[$letter]}; do
      n=$((n + 1)) L=${r%:*} I=${r#*:}
      echo "threat x$n $f $letter $L $I $((L * I)) An attacker number $n can do harm number $n"
      k=0
      for kind in ${kinds[$letter]}; do
        k=$((k + 1))
        echo "control c$n-$k x$n $kind control number $k for threat $n"
      done
      echo "attack x$n T1078"
      echo "attack x$n T1557"
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
