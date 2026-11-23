#!/bin/bash
# WRONG: the staff sign-in written at every rating, so one is bound to fit.
cat > ~/model.tm <<'EOF'
# The shop's checkout: threat model.
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

threat s1 f6 S 1 3 3 A thief with a staff laptop can sign in with its saved password
threat s2 f6 S 2 3 6 A former member of staff can sign in with a password nobody changed
threat s3 f6 S 3 1 3 A stranger can try passwords against the sign-in page for a while
threat t1 f6 S 3 3 9 An attacker on the internet can sign in to the back office with a guessed or stolen staff password and refund money to a card of their own
threat t2 f5 S 3 2 6 An attacker can post a forged payment result to the hook so that an unpaid order is sent out
threat t3 f1 T 2 3 6 An attacker who controls the analytics company's script can change the checkout page to show a card form of their own and collect card numbers
threat t4 f4 I 2 3 6 A contractor who can read the repository can take the provider API key from it and pay refunds out of the shop's account
threat t5 f9 I 2 3 6 An engineer who can read the log server can collect the card numbers and codes that phone orders leave in the request logs
threat t6 f6 R 2 2 4 A staff member can deny making a refund because the back office records refunds without the name of who made them

none f1 SRIDE the page is served over HTTPS from the CDN, which absorbs floods; it takes no sign-in
none f2 STRIDE the card goes straight to the provider over HTTPS and the provider protects its own form
none f3 STRIDE order requests carry no card data and the API checks every field and rate-limits
none f4 STRD the provider's API is authenticated both ways over HTTPS and logs every call
none f4 E the key can only create and refund payments for this shop
none f5 TRIDE the hook only reads a payment id and a status and looks nothing else up
none f6 TID HTTPS with a role check on every page behind the load balancer's rate limit
none f6 E every page checks the staff role of the signed-in person
none f7 STRIDE the back office calls the provider's API over HTTPS with its own restricted key
none f10 STRIDE a firewall lets only the orders API reach the stock port and every query is logged

accept s1 laptops are encrypted and a loss is reported the same day
control cs2 s2 access-proxy a leaver loses the proxy with their account
accept s3 the load balancer already slows a guesser down
control c1 t1 mfa every back-office sign-in needs a security key as well as the password
control c2 t2 signing check PayPoint's signature on every hook request with the signing secret
control c3 t3 integrity pin the script with a hash and allow only listed script sources
control c4 t4 secret-store move the key to the cloud's secrets manager, rotate it, and scan pushes
control c5 t5 minimise-data never log request bodies of the phone-order page; remove the old logs
control c6 t6 audit-log record every refund with the staff member, time, order and amount

top t1 t2 t3 t4 t5 s2
attack t1 T1110.004
attack t4 T1552.001

goal g1 t1 refund money to the attacker's own card
node n1 g1 or get into the back office
node n2 n1 and phish a staff member
leaf l1 n2 200 send a convincing sign-in page to ten staff
leaf l2 n2 50 use the captured password before it is changed
leaf l3 n1 100 try leaked passwords against the sign-in page
leaf l4 n1 2000 bribe a staff member
cheapest g1 100
EOF
