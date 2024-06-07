#!/bin/bash

source /app/www/vhosts/labchat.tnt.co.th/httpdocs-service/venv/bin/activate 

pm2 del service-content-searching
pm2 start