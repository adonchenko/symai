#!/bin/sh
EXIT_CODE=1
(while [ $EXIT_CODE -gt 0 ]; do
    $1 $2 $3 $4 $5 $6 $7 $8 $9
    # loops on error code: greater-than 0
    EXIT_CODE=$?
done)

