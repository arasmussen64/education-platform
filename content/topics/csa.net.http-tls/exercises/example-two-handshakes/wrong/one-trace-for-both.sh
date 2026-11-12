# Wrong: the TLS 1.2 file saved from the TLS 1.3 trace (no -tls1_2), so both
# files hold the same handshake.
mkdir -p ~/example
on office curl -sv https://www.shop.test/ -o /dev/null 2>&1 | grep 'ALPN: server accepted' > ~/example/alpn.txt
sleep 1 | on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_3 -trace > ~/example/trace13.txt 2>&1
grep -E '^    [A-Z][A-Za-z]+, Length' ~/example/trace13.txt | awk '{print $1}' | tr -d , | tr '\n' ' ' > ~/example/tls13.txt
cp ~/example/tls13.txt ~/example/tls12.txt
on office openssl s_client -connect 10.0.9.1:443 -servername api.shop.test < /dev/null 2> /dev/null | grep '^subject=' > ~/example/api-subject.txt
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -status < /dev/null > /dev/null 2>&1
sleep 1; on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -status < /dev/null 2> /dev/null | grep -E 'OCSP Response Status|Cert Status|Next Update' > ~/example/staple.txt
