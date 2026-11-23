#!/bin/bash
# WRONG: a model that lists everything everywhere and reads nothing of the
# design's facts. It draws and scopes the design as the solution does, then
# writes three threats under every letter of every flow, at three ratings,
# each with the same two controls for its letter and two techniques. It
# keeps every per-threat cap and chooses nothing.
cat > ~/model.tm <<'EOF'
zone internet   anyone on the internet
zone office     the shop's office network, staff laptops
zone provider   the payment provider, PayPoint
zone edge       the shop's storefront on the cloud's CDN
zone shop-net   the shop's cloud subnet 10.20.1.0/24
zone warehouse  the warehouse network 10.30.0.0/24

element customer   external internet   a customer's browser
element staff      external office     a staff member's laptop
element psp        external provider   PayPoint's card form and API
element web        process  edge       storefront and checkout page
element orders-api process  shop-net   orders, payments and refunds
element backoffice process  shop-net   staff pages: refunds, phone orders
element orders-db  store    shop-net   orders, last four digits, provider tokens
element app-logs   store    shop-net   the log server
element stock-db   store    warehouse  stock levels

flow f1  customer   web        browse and open the checkout page
flow f2  customer   psp        the card form posts the card to PayPoint
flow f3  web        orders-api create an order
flow f4  orders-api psp        create a payment, refund one
flow f5  psp        orders-api the payment-result hook
flow f6  staff      backoffice sign in, refunds, phone orders
flow f7  backoffice psp        a phone order's card number
flow f8  orders-api orders-db  read and write orders
flow f9  backoffice app-logs   request logs
flow f10 orders-api stock-db   reserve stock

scope web        impacting it serves the page that holds the provider's card form
scope orders-api cde no card data, but it shares an unfiltered subnet with backoffice
scope backoffice cde phone orders send card numbers through it
scope orders-db  cde same unfiltered subnet as backoffice, though it stores no card numbers
scope app-logs   cde request logs hold card numbers and codes today
scope stock-db   out firewalled, receives no card data and opens no connections back
EOF
declare -A rate=([I]="2:3 3:3 1:1" [S]="3:3 3:2 2:3" [T]="2:3 3:3 1:1" [R]="2:2 1:1 1:2" [D]="1:1" [E]="1:1")
declare -A kinds=([I]="secret-store minimise-data" [S]="mfa signing" [T]="integrity signing" [R]="audit-log signing" [D]="rate-limit" [E]="authz")
n=0 nines="" sixes=""
for f in f1 f2 f3 f4 f5 f6 f7 f8 f9 f10; do
  for letter in I S T R D E; do
    for r in ${rate[$letter]}; do
      n=$((n + 1)) L=${r%:*} I=${r#*:}
      echo "threat x$n $f $letter $L $I $((L * I)) An attacker number $n can do harm number $n"
      k=0
      for kind in ${kinds[$letter]}; do
        k=$((k + 1))
        echo "control c$n-$k x$n $kind control number $k for threat $n"
      done
      echo "attack x$n T1110"
      echo "attack x$n T1552"
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
