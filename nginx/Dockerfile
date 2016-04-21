FROM nginx
ADD sites-enabled/ /etc/nginx/sites-enabled/
RUN rm -v /etc/nginx/conf.d/default.conf
RUN rm -v /etc/nginx/nginx.conf
COPY conf/nginx.conf /etc/nginx/nginx.conf
ADD www/ /var/www/
RUN chown -R www-data:www-data /var/www/
EXPOSE 80 443
