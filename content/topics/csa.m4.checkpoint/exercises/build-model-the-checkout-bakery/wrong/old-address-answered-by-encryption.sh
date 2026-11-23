#!/bin/bash
# WRONG: the plain old address answered by encrypting something, not by TLS.
cat > ~/model.tm <<'EOF'
# Hartley's Bakery's online orders: threat model.
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

threat t1 f1 E 3 3 9 A customer who signs up for an account can open the admin pages and download every saved card
threat t2 f1 I 2 3 6 An attacker on a customer's cafe network can read the card numbers sent to the old plain address
threat t3 f1 T 3 2 6 A customer can change a cake's price in the order form before sending it and pay less
threat t4 f6 I 2 3 6 A developer can read whole card numbers in the saved cards while answering a question
threat t5 f6 R 2 2 4 A developer can deny looking at a customer's card because the database records no query

none f1 SRD a sign-in for every order, orders recorded by account, and a limit per address
none f3 STRIDE CardWorks' API authenticates both ways over HTTPS and logs every charge
none f5 STRIDE the kitchen firewall lets only orders in, and the list holds loaf counts only
none f6 STDE developers sign in with their own accounts over TLS

control c1 t1 authz the admin pages check the owner's admin role on every request
control c2 t2 encryption the old address only sends browsers on to HTTPS
control c3 t3 input-validation orders charges each cake's price from its own list, never the form's
control c4 t4 encryption encrypt the card numbers with a key the developers can't use
control c5 t5 audit-log record every query with the developer who made it

top t1 t2 t3 t4
attack t1 T1078
attack t2 T1557

goal g1 t1 download every saved card
node n1 g1 or open the admin pages
node n2 n1 and sign up and find the pages
leaf l1 n2 0 sign up for a free account
leaf l2 n2 10 guess the admin pages' address
leaf l3 n1 300 phish the owner's password
cheapest g1 10
EOF
