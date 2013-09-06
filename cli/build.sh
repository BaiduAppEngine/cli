#!/bin/sh

WORKPATH=`dirname $0`

if [ ! -d ${WORKPATH}/output ]; then
    mkdir ${WORKPATH}/output
fi

tar czvf cli.tar.gz *
mv cli.tar.gz ${WORKPATH}/output/

