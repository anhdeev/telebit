openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 365 -out public.pem -subj "/C=US/ST=California/L=SanJoe/O=Viosoft/CN=35.197.140.7"
mv private.key public.pem ../ssl
