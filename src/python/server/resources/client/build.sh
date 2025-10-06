#!/bin/bash
mkdir ./src/app/backup
cp -y ./src/app/app.ts ./src/app/backup
sed -i "s/CORE_URL/${CORE_HOST}:${CORE_PORT}/g" ./src/app/app.ts
ng build --configuration=production
