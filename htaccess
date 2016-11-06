---
layout: none
permalink: .htaccess
---

RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L] 

RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} Gemfile
RewriteCond %{REQUEST_FILENAME} Gemfile.lock
RewriteRule . /index.html [L] 

RewriteCond %{HTTP_HOST} !^$ 
RewriteCond %{HTTP_HOST} !^www\. [NC]
RewriteCond %{HTTPS}s ^on(s)|
RewriteRule ^ http%1://www.%{HTTP_HOST}%{REQUEST_URI} [R=301,L]