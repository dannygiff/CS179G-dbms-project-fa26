#!/bin/bash    
#Example Usage:  ./playercount.sh "Left 4 Dead 2"    
# appid=$(curl -s https://api.steampowered.com/ISteamApps/GetAppList/v1/ | jq ".applist.apps[] | select(.name==\"$1\")" | jq '.appid')    
# curl -s https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid="$appid" | jq '.response.player_count'
mapfile lines < /home/cs179g/repo/src/steamkey.env
export "${lines[@]}"
appListJson=$(curl -s GET https://api.steampowered.com/IStoreService/GetAppList/v1/?key=$STEAM_KEY | jq ".applist.apps[] | select(.name==\"$1\")")
# jq "select(.name==\"$1\")" $appListJson | jq '.appid'