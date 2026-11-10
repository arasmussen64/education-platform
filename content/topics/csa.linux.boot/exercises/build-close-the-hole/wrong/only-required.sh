# Wrong: tokens are required, but the shop's client was never updated, so it
# still sends a plain GET and now gets a 401: the hole is closed but the
# legitimate client is broken.
lab-imds-options --tokens required
