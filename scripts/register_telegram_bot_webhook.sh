BOT_KEY=463733841:AAHURJK64srQaqVrnF9hf2iU5_BOG2SVbrc
SERVER_DOMAIN=35.197.140.7
curl \
-F "url=https://${SERVER_DOMAIN}/webhook" \
-F "certificate=@/home/dva912/telebit/ssl/public.pem" \
-F "allowed_updates[]=message" \
https://api.telegram.org/bot${BOT_KEY}/setWebhook

