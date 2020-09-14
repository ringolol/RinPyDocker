FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY certificate.crt /etc/ssl/certificate.crt
COPY private.key /etc/ssl/private.key