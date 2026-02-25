#!/bin/sh

#colous
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

#check input
if [ $# -ne 1 ]; then
	printf "${RED}Error:${RESET} wrong number of arguments\n"
	printf "${YELLOW}how to use:${RESET} $0 <bit.ly link>\n"
	exit 1
fi

LINK=$1

#check if the link is valid
#grep -qE : -q: quiet return 0/1/2, -E: extended regex
if ! echo "$LINK" | grep -qE '^(https?://)?bit\.ly/[a-zA-Z0-9]+$'; then
	printf "${RED}Error:${RESET} invalid bit.ly link\n"
	exit 1
fi

#fetch the original URL
#curl -sI -s: silent -I: fetch only headers
URL=$(curl -sI $LINK | grep -i ^location: | cut -d " " -f 2)

echo $URL
