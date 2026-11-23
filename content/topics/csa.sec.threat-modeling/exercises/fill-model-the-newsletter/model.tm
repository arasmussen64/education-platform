# The shop's newsletter sign-up: a threat model with eight gaps (___).
# Fill each gap from ~/design.md, and change nothing else.

# What are we working on
zone internet anyone on the internet
zone shop the shop's own cloud network
zone mailer-co the mailing company
element visitor external internet a visitor's browser or phone
element signup-api process shop the sign-up API
element subscribers-db ___ shop subscribers' email addresses
element mailer external ___ the mailing company's servers
flow f1 visitor signup-api type an email address to subscribe
flow f2 signup-api subscribers-db read and write the list
flow f3 signup-api mailer hand over an email to deliver
flow f4 mailer signup-api bounce reports to /hooks/bounce

# What can go wrong
threat t1 f1 S 3 1 ___ A visitor can type in someone else's address, and that person gets an email they never asked for
none f1 TRIDE HTTPS, the load balancer's limit, and an address joins the list only when its link is opened
none f3 STRIDE the mailing company proves itself with its certificate, and the API key travels only inside HTTPS
threat t2 f4 ___ 3 3 9 An attacker on the internet can pretend to be the mailing company and post made-up bounce reports, and real subscribers are taken off the list
none f4 ___ HTTPS in transit, a report holds one email address, the load balancer limits each address, and the hook can take an address off the list and nothing else
top t2

# What are we going to do about it
accept t1 the address is added only after its owner opens the link
control c1 t2 ___ refuse a bounce report that the mailing company did not send

# The worst risk, as an attack tree and an abuse case
goal g1 t2 take real subscribers off the list
leaf l1 g1 5 post made-up bounce reports to the hook from anywhere
node n1 g1 and send the reports from inside the mailing company
leaf l2 n1 400 phish a mailing company employee
leaf l3 n1 150 find the server that sends the reports
leaf l4 g1 3000 bribe a shop administrator to empty the list
cheapest g1 ___
abuse a1 t2 As an attacker, I post bounce reports for addresses I collected so that ___
test x1 a1 post a report with no valid signature and expect 401 and an unchanged list
