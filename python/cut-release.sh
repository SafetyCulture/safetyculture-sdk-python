#!/bin/sh
VERSION="$1"

if [ -d "dist/" ]
then
  rm -rf dist/
fi

mkdir dist/
mkdir dist/tmp
cd dist/tmp/

git clone --branch $VERSION https://github.com/SafetyCulture/safetyculture_python

zip -r ../safetyculture-exporter-python-$VERSION.zip . -x "*.git*"
rm -rf ../tmp/
