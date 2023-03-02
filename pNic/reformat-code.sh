#! /bin/bash

LL=160

black --line-length "$LL" .
pylama --max-line-length="$LL" . |
awk '
/Clickhouse\// { next }
{ print }
'
