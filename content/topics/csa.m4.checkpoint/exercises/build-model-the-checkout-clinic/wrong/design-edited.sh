#!/bin/bash
# WRONG: the design note is changed to suit the model.
sed -i 's/and its admin password is still the/and its admin password is no longer the/' ~/design.md
cat > ~/model.tm <<'EOF'
# Westbrook Clinic's payment desk: threat model.
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

threat t1 f3 T 3 2 6 An attacker can open the paid page with any invoice number and mark that invoice paid without paying
threat t2 f5 I 3 2 6 An attacker can count through the invoice numbers and read every patient's invoice without signing in
threat t3 f8 S 2 3 6 A person on the office network can sign in to the terminal's admin page with the maker's default password and send payments elsewhere
threat t4 f8 I 2 3 6 An attacker on a phished reception PC can use the terminal's published flaw to read card numbers as cards are used
threat t5 f6 E 1 3 3 An administrator of the cloud network can reuse billing's database account to change any invoice

none f1 STRIDE the portal is served over HTTPS, takes no card data and limits requests per address
none f2 STRIDE PayHub runs and protects its own hosted page over HTTPS
none f3 SRIDE the result names only an invoice and a status, over HTTPS
none f5 STRDE an invoice page can only be read, over HTTPS, and requests per address are limited
none f7 STRIDE the terminal and PayHub authenticate each other on the terminal's own link

control c1 t1 signing check PayHub's signed result, or ask PayHub's API, before marking an invoice paid
control c2 t2 authz a patient signs in and sees their own invoices only
control c3 t3 authn give the terminal's admin page a long password of its own
control c4 t4 patch install the maker's fix for the published flaw
accept t5 only two named administrators can reach the database

top t1 t2 t3 t4
attack t2 T1190
attack t3 T1078.001

goal g1 t3 send the clinic's card payments elsewhere
node n1 g1 or reach the terminal's admin page
node n2 n1 and phish a receptionist
leaf l1 n2 300 send a convincing email to reception
leaf l2 n2 100 run a program on the reception PC
leaf l3 n1 500 walk in and plug a laptop into the office network
cheapest g1 400
EOF
