# Riverside Parcels: the drivers' app

Riverside Parcels delivers parcels. Its drivers use a phone app that talks
to Riverside's own API. This note describes the system as it is today.

## The parts

- `driver`: a driver's phone, anywhere on the internet.
- `app`: the drivers' API. Riverside runs it in its own cloud network, the
  depot network.
- `parcels-db`: the database of parcels, addresses and doorstep photos. It
  is the cloud's managed database service, reached only from the depot
  network.
- `maps`: the maps company's servers. The maps company runs them.

## The flows

- `f1`, from `driver` to `app`: a driver signs in and updates a delivery.
  The API's address is public. Drivers sign in with a password, and nothing
  else.
- `f2`, from `app` to `parcels-db`: the API reads and writes parcels.
- `f3`, from `maps` to `app`: the maps company posts a report to
  `/hooks/roads` when a road closes, and the API sends the drivers on that
  road another way. The hook takes a report from any caller.

## Already in place

HTTPS everywhere. A load balancer in front of the API limits how many
requests one address can send. Every request the API takes is checked
against the signed-in driver's role.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first, or with a password that was guessed or phished.
2: it needs something first, such as a driver's unlocked phone or a
supplier's system. 1: it needs an administrator's rights.

Impact. 3: parcels go to the wrong person, or customers' addresses or
photos are exposed. 2: deliveries are late or a delivery record is false.
1: a nuisance.
