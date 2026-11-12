# Wrong: the staple saved from the first handshake after nginx restarts,
# which goes without one ("no response sent").
mkdir -p ~/example
on office curl -sv https://www.shop.test/ -o /dev/null 2>&1 | grep 'ALPN: server accepted' > ~/example/alpn.txt
sleep 1 | on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_3 -trace > ~/example/trace13.txt 2>&1
grep -E '^    [A-Z][A-Za-z]+, Length' ~/example/trace13.txt | awk '{print $1}' | tr -d , | tr '\n' ' ' > ~/example/tls13.txt
sleep 1 | on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_2 -trace > ~/example/trace12.txt 2>&1
grep -E '^    [A-Z][A-Za-z]+, Length' ~/example/trace12.txt | awk '{print $1}' | tr -d , | tr '\n' ' ' > ~/example/tls12.txt
on office openssl s_client -connect 10.0.9.1:443 -servername api.shop.test < /dev/null 2> /dev/null | grep '^subject=' > ~/example/api-subject.txt
sudo systemctl restart nginx@web; sleep 1
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -status < /dev/null 2> /dev/null | grep -E 'OCSP response:|OCSP Response Status|Cert Status' > ~/example/staple.txt
