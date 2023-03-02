#! /usr/bin/env bash
# --data-binary @data.json

# http://localhost:82/api/aNode/NodeType/?name=aCompany

HOST_PORT="localhost:82"

USER="admin"
PASS="--------------"

URI="aNode/NodeType/"

H_JSON='--header "Content-Type: application/json"'

makeUrl()
{
    local uri="$1"
    echo "http://$USER:$PASS@$HOST_PORT/api/$uri"
}

getUriList()
{
    cat <<! |
    aNode/NodeType/
    aNode/EdgeType/
    aNode/Edge/
    aNode/Node/
!
    awk '
    /^[ \s]*#/ { next }
    /^[ \s]*;/ { next }
    /^[ \s]*$/ { next }
    { print $1 }
    '
}

oneRunGet()
{
    local uri="$1"
    local url=$( makeUrl "$uri" )
    curl -X GET "$url"
    echo ""
}

oneRunPost()
{
    local uri="$1"
    local data="$2"

    local url=$( makeUrl "$uri" )

    echo "$url"
    # curl -v -H "$H_JSON" -X "POST" -d "$data" "$url.json"
    set -x
    curl -v \
    -H 'Content-Type: application/json'   -H 'Accept: application/json' \
    -X "POST" --data-binary @/tmp/data.txt "$url"
    set +x
    echo ""
}

readAllData()
{
    getUriList |
    while read uri
    do
        oneRunGet "$uri"
    done
}

testCreateNodeType()
{
    local nt="$1"

    uri="aNode/NodeType/"
    echo '{"name": "test12345","description": "test1234"}' >/tmp/data.txt

    oneRunPost "$uri"
}

main()
{
    readAllData
    testCreateNodeType "test123"
    readAllData
}

main
