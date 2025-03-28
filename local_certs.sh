rm -rf demoCA
mkdir demoCA
echo 01 > demoCA/serial
touch demoCA/index.txt.attr
touch demoCA/index.txt

# Generate .rnd if it does not exist
openssl rand -out /root/.rnd -hex 256

# CA self certificate
openssl req  -new -batch -x509 -days 3650 -nodes -newkey rsa:1024 -out /etc/open5gs/tls/cacert.pem -keyout cakey.pem -subj /CN=ca.EPC_DOMAIN/C=KO/ST=Seoul/L=Nowon/O=Open5GS/OU=Tests

#mme
openssl genrsa -out /etc/open5gs/tls/mme.key.pem 1024
openssl req -new -batch -out mme.csr.pem -key /etc/open5gs/tls/mme.key.pem -subj /CN=mme.epc.mnc334.mcc230.3gppnetwork.org/C=KO/ST=Seoul/L=Nowon/O=Open5GS/OU=Tests
openssl ca -cert /etc/open5gs/tls/cacert.pem -days 3650 -keyfile cakey.pem -in mme.csr.pem -out /etc/open5gs/tls/mme.cert.pem -outdir . -batch

rm -rf demoCA
rm -f 01.pem 02.pem 03.pem 04.pem
rm -f cakey.pem
rm -f mme.csr.pem