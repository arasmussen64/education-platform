# A risk of 6 left off the top line.
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
none f1 STRIDE a patient proves their phone number with a code sent to it and reaches only their own appointments, over HTTPS and behind the load balancer's limit
threat t1 f2 S 3 3 9 An attacker on the internet can sign in to the staff pages with a phished password and read every patient's bookings
threat t2 f2 R 2 2 4 A member of staff can deny changing a booking because nothing records who made a change
none f2 TIDE HTTPS, the load balancer's limit, a role check on every staff page and a web user with no administrator rights
threat t3 f4 S 3 2 6 An attacker on the internet can post a made-up STOP reply for a patient's phone number, and that patient's appointments are cancelled
none f4 TRIDE HTTPS in transit, a report holds a phone number and a word, the load balancer limits each address, and the SMS company keeps its own record of what it sent
none f5 STRIDE the site writes with a key of its own over HTTPS, and nobody else may write to the bucket
threat t4 f6 I 3 3 9 An outsider who works out a file's link can download the export, with patients' names and phone numbers in it
none f6 STRDE the analyst only reads, nobody but the site may write, and the cloud provider keeps the storage service running
top t1 t4
control c1 t1 mfa a code from the staff member's phone as well as the password
control c2 t2 audit-log record who changed each booking, and when
control c3 t3 signing switch on the SMS company's signing secret and refuse a report without a valid signature
control c4 t4 authz turn link sharing off and give the analyst a sign-in of their own
attack t1 T1078
attack t4 T1530
goal g1 t4 read patients' names and phone numbers
leaf l1 g1 10 work out the link of last night's export file
node n1 g1 and get in through the staff pages
leaf l2 n1 200 phish a receptionist's password
leaf l3 n1 50 sign in and page through the bookings
leaf l4 g1 5000 bribe a member of staff to copy the list
cheapest g1 10
abuse a1 t1 As an attacker, I sign in with a receptionist's phished password so that I can read every patient's bookings
test x1 a1 sign in with a right password and no code, and expect to be refused
abuse a2 t4 As an outsider, I open the export's link without signing in so that I get patients' names and phone numbers
test x2 a2 ask for last night's file with no sign-in and expect 403
abuse a3 t3 As a prankster, I post STOP replies for phone numbers I know so that those patients lose their appointments
test x3 a3 post a report with no valid signature and expect 401 and an unchanged booking
EOF
