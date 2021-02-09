#!/bin/sh

while true; do
  if [ "$(pidof ices2)" ] 
  then
    echo "running..."
  else
    sudo ices2 /home/tvaz/radiopyo/conf/ices-playlist.xml
  fi
sleep 5
done
