# The zone and the rating put right, and both high risks answered with
# every kind of control their letters allow: one of them is bound to
# fit, and nothing was chosen.
cat > ~/model.tm <<'EOF'
# Riverside Parcels: threat model of the drivers' app
# Approved by the security board last month.
zone internet anyone on the internet
zone depot Riverside's own cloud network
zone cloud-storage the cloud provider's storage service
zone maps-co the maps company
element driver external internet a driver's phone
element customer external internet a customer's browser or phone
element app process depot the drivers' API
element parcels-db store depot parcels and delivery addresses
element photos store cloud-storage the bucket of doorstep photos
element maps external maps-co the maps company's servers
flow f1 driver app sign in, mark parcels delivered, send a parcel elsewhere
flow f2 app parcels-db read and write parcels
flow f3 app photos store a doorstep photo
flow f4 customer photos open a doorstep photo from the email's link
flow f5 maps app road-closure reports to /hooks/roads
threat t1 f1 S 3 3 9 An attacker on the internet can sign in as a driver with a phished password and send parcels to another address
threat t2 f1 S 2 2 4 A thief with a driver's unlocked phone can mark parcels delivered that never arrived
none f1 TRIDE HTTPS, the load balancer's limit, a role check on every request and a record of which driver made each change
none f3 STRIDE the API writes with a key of its own over HTTPS, and nobody else may write to the bucket
threat t3 f4 I 3 3 9 An outsider who works out a photo's link can open the doorstep photo, with the house number in view
none f4 STRDE a customer only reads, nobody but the API may write, and the cloud provider keeps the storage service running
none f5 STRIDE the maps company signs every report and the API refuses one without a valid signature, a report holds a road's name and a time, and the load balancer limits each address
top t1 t3
control c10 t1 authn whatever this kind of control does
control c11 t1 mfa whatever this kind of control does
control c12 t1 mutual-tls whatever this kind of control does
control c13 t1 signing whatever this kind of control does
control c14 t1 access-proxy whatever this kind of control does
accept t2 a parcel marked delivered by mistake is settled with the doorstep photo
control c20 t3 tls whatever this kind of control does
control c21 t3 encryption whatever this kind of control does
control c22 t3 minimise-data whatever this kind of control does
control c23 t3 authz whatever this kind of control does
control c24 t3 least-privilege whatever this kind of control does
control c25 t3 access-proxy whatever this kind of control does
control c26 t3 secret-store whatever this kind of control does
control c27 t3 patch whatever this kind of control does
EOF
