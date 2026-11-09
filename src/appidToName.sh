#!/bin/bash    
#Example Usage:  ./playercount.sh "Left 4 Dead 2"    
# appid=$(curl -s https://api.steampowered.com/ISteamApps/GetAppList/v1/ | jq ".applist.apps[] | select(.name==\"$1\")" | jq '.appid')    
# curl -s https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid="$appid" | jq '.response.player_count'
curl -s GET https://api.steampowered.com/IStoreService/GetAppList/v1/ 