# Northfield Clinic: the booking service

Northfield Clinic lets its patients book appointments online, reminds
them by text message, and sends a file of each day's bookings to the
accounting firm that prepares its monthly figures. This note describes the
booking service as it is today.

## The parts

- `patient`: a patient's browser or phone, anywhere on the internet.
- `staff`: a receptionist's or a doctor's own laptop or phone, at the
  clinic, at home or on the road.
- `analyst`: the laptop of the analyst at the accounting firm.
- `web`: the booking site and its staff pages. The clinic runs it on a
  server of its own, in its own cloud network.
- `bookings-db`: the database of patients' names, phone numbers and
  appointments. It is the cloud's managed database service, reached only
  from the clinic's network.
- `sms-gateway`: the SMS company's servers, which send the clinic's
  reminders. The SMS company runs them.
- `exports`: a bucket in the cloud's storage service, where the nightly
  export files are kept. The cloud provider serves its files at a public
  address.

## The flows

- `f1`, from `patient` to `web`: a patient books, changes or cancels an
  appointment. A patient gives their phone number, types the code the
  site sends to it, and then reaches their own appointments only.
- `f2`, from `staff` to `web`: a member of staff signs in to the staff
  pages and changes bookings. The staff pages are at the same public
  address as the booking site. Staff sign in with a password, and nothing
  else. The site saves each change to a booking, and nowhere records
  which member of staff made it.
- `f3`, from `web` to `bookings-db`: the site reads and writes bookings.
- `f4`, from `sms-gateway` to `web`: the SMS company posts a report to
  `/hooks/sms` when a reminder is delivered and when a patient replies to
  one. A reply of `STOP` cancels that phone number's appointments. The
  hook takes a report from any caller: the SMS company offers a signing
  secret for its reports, and the clinic has not switched it on.
- `f5`, from `web` to `exports`: each night the site writes a file of the
  day's bookings, with names and phone numbers, to the bucket, using a
  key of its own. Nobody else may write there.
- `f6`, from `analyst` to `exports`: the analyst downloads the files. The
  bucket's link sharing is on: a file opens for anyone who has its link,
  with no sign-in. Nothing about a link is secret: it is the bucket's
  public address followed by `bookings-` and the day's date.

## Already in place

HTTPS everywhere. A load balancer in front of `web` limits how many
requests one address can send. `web` runs as a user with no administrator
rights. Every staff page checks the signed-in member's role.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first, or with a password that was guessed or phished.
2: it needs something first, such as a patient's unlocked phone, a place
among the clinic's staff, or a place inside a supplier's systems. 1: it
needs the clinic's administrator rights.

Impact. 3: patients' names, phone numbers or appointments are exposed, or
many patients' appointments are changed or cancelled. 2: one patient's
appointments are changed or cancelled, or a record of who did something
is missing or false. 1: a nuisance, with nothing lost.
