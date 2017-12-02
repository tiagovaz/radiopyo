#!/bin/sh

while true; do
  if [ "$(pidof ices2)" ] 
  then
    echo "running..."
  else
    ices2 /xxxxxx/ices-playlist.xml
  fi
sleep 5
done
