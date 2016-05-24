#!/bin/bash
mitie_zipped=mitie-v0.2-python-2.7-windows-or-linux64.zip
mitie_dir=mitie-v0.2-python-2.7-windows-or-linux64

if [ ! -f $mitie_zipped ];
then
    wget http://downloads.sourceforge.net/project/mitie/binaries/mitie-v0.2-python-2.7-windows-or-linux64.zip
fi

if [ ! -d $mitie_dir ];
then
    unzip $mitie_zipped
fi
