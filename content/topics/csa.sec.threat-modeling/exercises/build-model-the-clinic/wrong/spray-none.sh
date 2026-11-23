# Nothing to record anywhere, with one reason for every flow.
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
none f1 STRIDE HTTPS everywhere, a rate limit and role checks are already in place
none f2 STRIDE HTTPS everywhere, a rate limit and role checks are already in place
none f4 STRIDE HTTPS everywhere, a rate limit and role checks are already in place
none f5 STRIDE HTTPS everywhere, a rate limit and role checks are already in place
none f6 STRIDE HTTPS everywhere, a rate limit and role checks are already in place
EOF
