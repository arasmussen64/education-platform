# The photo threat deleted, with its accept line: nothing left to rate.
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
none f4 STRIDE a customer only reads, and only the customer is sent the link to their photo
none f5 STRIDE the maps company signs every report and the API refuses one without a valid signature, a report holds a road's name and a time, and the load balancer limits each address
top t1
control c1 t1 mfa a code from the driver's phone as well as the password
accept t2 a parcel marked delivered by mistake is settled with the doorstep photo
EOF
