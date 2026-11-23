# /etc/openbao/openbao.hcl: the lab's OpenBao server, one node on this machine.
# Part of the base (content/lab-bases/vault): a lab that needs another
# setting ships its own copy of this file.

# No web console: the labs use the command line, as scripts do.
ui = false

# Where OpenBao keeps everything it stores, encrypted. pebbledb is the
# package's own default store (2.7 has no "file" store any more).
storage "pebbledb" {
  path = "/opt/openbao/data"
}

# Plain HTTP, and only for programs on this machine. A real server listens
# with TLS; here nothing leaves the loopback interface.
listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = true
}
api_addr = "http://127.0.0.1:8200"

# OpenBao encrypts its store under a key that it must be given at every
# start ("unsealing"). The static seal reads that key from a file, which
# stands in for a cloud key service's auto-unseal. The file is made at the
# machine's first boot (lab-bao-key.service); it is in no image.
seal "static" {
  current_key_id = "lab-1"
  current_key    = "file:///etc/openbao/unseal.key"
}

# Every request and answer, one JSON line each, with secret values replaced
# by an HMAC of them. OpenBao 2.7 lets an audit device be declared only
# here, never through the API.
audit "file" "file" {
  description = "The lab's audit log."
  options {
    file_path = "/var/log/openbao/audit.log"
  }
}
