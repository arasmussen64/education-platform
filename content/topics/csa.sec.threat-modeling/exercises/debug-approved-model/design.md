# Riverside Parcels: the drivers' app

Riverside Parcels delivers parcels. Its drivers use a phone app that talks
to Riverside's own API, and a customer gets an email with a photo of the
parcel on their doorstep. This note describes the system as it is today.

## The parts

- `driver`: a driver's phone, anywhere on the internet.
- `customer`: a customer's browser or phone, anywhere on the internet.
- `app`: the drivers' API. Riverside runs it on its own servers, in its
  own cloud network, the depot network.
- `parcels-db`: the database of parcels and delivery addresses. Riverside
  runs it too, on a server in the depot network.
- `photos`: a bucket in the cloud's storage service, where the doorstep
  photos are kept. The cloud provider serves its files at a public
  address.
- `maps`: the maps company's servers. The maps company runs them.

## The flows

- `f1`, from `driver` to `app`: a driver signs in, marks parcels
  delivered, and sends a parcel to another address when a customer asks.
  The API's address is public. Drivers sign in with a password, and
  nothing else. The API writes each sign-in to a log, with its time and
  the address it came from, and records which driver made each change.
- `f2`, from `app` to `parcels-db`: the API reads and writes parcels.
- `f3`, from `app` to `photos`: the API stores each doorstep photo in the
  bucket, using a key of its own. Nobody else may write there.
- `f4`, from `customer` to `photos`: a customer opens the photo of their
  parcel from the link in the delivery email. A photo opens for anyone
  who has its link, with no sign-in. Nothing about a link is secret: it is
  the bucket's public address followed by the parcel's tracking number,
  and tracking numbers run in order.
- `f5`, from `maps` to `app`: when a road closes, the maps company posts a
  report (a road's name and a time) to `/hooks/roads`, and the API sends
  the drivers on that road another way. The maps company signs every
  report, and the API refuses a report without a valid signature.

## Already in place

HTTPS everywhere. A load balancer in front of the API limits how many
requests one address can send. Every request the API takes is checked
against the signed-in driver's role.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first, or with a password that was guessed or phished.
2: it needs something first, such as a driver's unlocked phone or a place
inside a supplier's systems. 1: it needs Riverside's administrator rights.

Impact. 3: parcels go to the wrong person, or customers' addresses or
photos are exposed. 2: deliveries are late, or a delivery record is
false. 1: a nuisance, with nothing lost.
