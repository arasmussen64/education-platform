#!/bin/bash
# WRONG: the shared PIN answered with TLS.
cat > ~/model.tm <<'EOF'
# Quickprint's counter and uploads: threat model.
zone internet  anyone on the internet
zone provider  PayLink, the payment provider
zone floor     the shop floor's network
zone cloud     Quickprint's cloud account

element customer     external internet  a customer's browser
element psp          external provider  PayLink's payment page, readers and API
element till-pc      process  floor     the till at the counter, with its card reader
element print-server process  floor     the print room's job server
element directory    process  cloud     the staff sign-in service
element files        store    cloud     the bucket of customers' uploads

flow f1 customer     files        upload a file
flow f2 till-pc      psp          a card payment at the counter
flow f3 till-pc      directory    staff sign in to the till
flow f4 print-server files        fetch a job's files
flow f5 till-pc      print-server send a paid job to print
flow f6 customer     psp          pay by PayLink's emailed link

scope till-pc      cde card details pass through it from the reader to PayLink
scope print-server cde it shares the till's network with nothing filtering
scope directory    impacting it signs staff in to the till, a card system
scope files        out it holds print files only, in the cloud, apart from the till

threat t1 f1 I 3 2 6 An attacker can list the bucket and download every customer's files without an account
threat t2 f3 S 2 3 6 A former member of staff can sign in to the till with the shared PIN and refund money to their own card
threat t3 f5 T 2 1 2 A person on the shop floor network can send the print server a job nobody paid for

none f1 STRDE uploads go over HTTPS to a bucket that only takes new files
none f2 STRIDE the reader and PayLink authenticate each other on their own link
none f3 TRIDE the till asks over HTTPS and the sign-in service keeps a log
none f4 STRIDE the print server reads with a key that can only read
none f6 STRIDE the customer pays on PayLink's own page over HTTPS

control c1 t1 authz the bucket gives each file only to the customer who uploaded it
control c2 t2 tls each member of staff signs in as themselves, removed when they leave
accept t3 a stray job wastes paper, and the print room sees it

top t1 t2
attack t1 T1530
attack t2 T1078

goal g1 t2 refund money to the attacker's own card
node n1 g1 or learn the PIN
node n2 n1 and watch the counter
leaf l1 n2 20 stand in the queue
leaf l2 n2 0 read the PIN as it is typed
leaf l3 n1 50 ask a former colleague
cheapest g1 20
EOF
