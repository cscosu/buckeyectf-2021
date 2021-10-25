#!/usr/bin/env sh

rm -rf dist
mkdir dist

cd deploy
docker-compose up -d --build --remove-orphans
docker cp deploy_app_1:/home/ctf/app/chall .
docker-compose down
rsync -avzP . ../dist --exclude=".gdb_history"
cd ..
sed -i '' 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' dist/sp22.txt

zip -r dist.zip dist/*
rm -rf dist
mkdir dist
name=${PWD##*/}
mv dist.zip dist/$name.zip
