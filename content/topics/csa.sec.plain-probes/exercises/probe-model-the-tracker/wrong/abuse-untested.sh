# An abuse case for the forged report with no test: a story nobody tries.
cat > ~/model.tm <<'EOF'
zone internet anyone on the internet
zone depot Riverside's cloud network
zone maps-co the maps company
element driver external internet a driver's phone
element app process depot the drivers' API
element parcels-db store depot parcels and doorstep photos
element maps external maps-co the maps company's servers
flow f1 driver app sign in and update a delivery
flow f2 app parcels-db read and write parcels
flow f3 maps app road-closure reports
threat t1 f1 S 3 3 9 An attacker on the internet can sign in as a driver with a phished password and redirect parcels
threat t2 f3 S 3 2 6 An attacker can post a made-up road closure to the hook so that drivers are sent the long way round
threat t3 f1 R 2 1 2 A driver can deny marking a parcel delivered because the app keeps no record of who did
none f1 TIDE HTTPS, a role check on every request and the load balancer's rate limit
none f3 TRIDE the hook reads a road name and a time and looks nothing else up
control c1 t1 mfa a code from the driver's phone as well as the password
control c2 t2 signing check the maps company's signature on every report
accept t3 a wrong delivery mark is settled with the photo
top t1 t2
attack t1 T1078
goal g1 t1 redirect a parcel
node n1 g1 or get a driver's session
node n2 n1 and phish a driver
leaf l1 n2 100 send a fake sign-in page
leaf l2 n2 20 use the password the same day
leaf l3 n1 500 bribe a driver
cheapest g1 120
abuse a1 t1 As an attacker, I sign in with a phished password so that I can redirect parcels
test x1 a1 sign in with a known password and no code, and expect a refusal
abuse a2 t2 As a rival, I post made-up closures so that deliveries run late
EOF
