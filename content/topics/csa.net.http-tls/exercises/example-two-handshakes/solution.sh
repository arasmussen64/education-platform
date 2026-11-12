netlab show
mkdir -p ~/example
on office curl -sv https://www.shop.test/ -o /dev/null 2>&1 | grep -E 'ALPN|SSL connection|HTTP/'
on office curl -sv --http1.1 https://www.shop.test/ -o /dev/null 2>&1 | grep -E 'ALPN|HTTP/'
on office curl -sv https://www.shop.test/ -o /dev/null 2>&1 | grep 'ALPN: server accepted' | tee ~/example/alpn.txt
sleep 1 | on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_3 -trace > ~/example/trace13.txt 2>&1
grep -E '^    [A-Z][A-Za-z]+, Length' ~/example/trace13.txt | awk '{print $1}' | tr -d , | tr '\n' ' ' | tee ~/example/tls13.txt; echo
grep -B4 '^    Certificate, Length' ~/example/trace13.txt
sleep 1 | on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_2 -trace > ~/example/trace12.txt 2>&1
grep -E '^    [A-Z][A-Za-z]+, Length' ~/example/trace12.txt | awk '{print $1}' | tr -d , | tr '\n' ' ' | tee ~/example/tls12.txt; echo
grep -B4 '^    Certificate, Length' ~/example/trace12.txt
on web timeout 4 tcpdump -i eth0 -nn -A -s 0 tcp port 443 > ~/example/wire13.txt 2> /dev/null & sleep 1; on office curl -s --tlsv1.3 https://www.shop.test/ > /dev/null; wait
grep -o www.shop.test ~/example/wire13.txt | wc -l
on web timeout 4 tcpdump -i eth0 -nn -A -s 0 tcp port 443 > ~/example/wire12.txt 2> /dev/null & sleep 1; on office curl -s --tlsv1.2 --tls-max 1.2 https://www.shop.test/ > /dev/null; wait
grep -o www.shop.test ~/example/wire12.txt | wc -l
on office openssl s_client -connect 10.0.9.1:443 -servername www.shop.test < /dev/null 2> /dev/null | grep -A8 '^Certificate chain'
on office openssl s_client -connect 10.0.9.1:443 -servername api.shop.test < /dev/null 2> /dev/null | grep '^subject=' | tee ~/example/api-subject.txt
on office openssl s_client -connect 10.0.9.1:443 -servername old.shop.test < /dev/null 2>&1 | grep -m 1 -o -E 'tlsv1 (alert )?[a-z ]*[a-z]'
on office openssl s_client -connect 10.0.9.1:443 -noservername < /dev/null 2>&1 | grep -m 1 -o -E 'tlsv1 (alert )?[a-z ]*[a-z]'
on web grep -n -E 'listen|server_name|ssl_reject|ssl_certificate ' /etc/nginx/sites-available/shop
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -tls1_1 -cipher 'DEFAULT@SECLEVEL=0' < /dev/null 2>&1 | grep -m 1 -o -E 'tlsv1 (alert )?[a-z ]*[a-z]'
on web grep ssl_protocols /etc/nginx/nginx.conf
sudo systemctl restart nginx@web; sleep 1
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -status < /dev/null 2> /dev/null | grep -E 'OCSP response:|OCSP Response Status|Cert Status'
sleep 1; on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -status < /dev/null 2> /dev/null | grep -E 'OCSP Response Status|Cert Status|Next Update' | tee ~/example/staple.txt
on web grep -E 'ssl_stapling|resolver' /etc/nginx/sites-available/shop
ls ~/example
