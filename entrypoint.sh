#!/bin/bash

# Start the flask server
echo "Starting Flask Server..."
echo "Mic check.. is this thing on?" >> /app/storage/web.log
nohup python -m flask --app website run --host=0.0.0.0 > /app/storage/web.log 2>&1 &
echo "Flask Server Started!"

while true; do
  echo "Getting Posts..."
  #python get_posts.py
  sleep 60
  echo "Notifying Users..."
  python notifier.py
  sleep 60
done