wget https://github.com/Patataman/DMyE1/releases/download/0.2.0/data_librebor.zip
unzip data_librebor.zip
echo "Deleting dme database"
mongo dme --eval "db.dropDatabase()"
echo "Indexing backup"
mongoimport --db dme --collection=contracts dme_contracts.json
mongoimport --db dme --collection=company dme_company.json
mongoimport --db dme --collection=electoral_list dme_electoral_list.json
mongoimport --db dme --collection=offshore dme_offshore.json
echo "removing .zip"
rm data_librebor.zip
rm dme_*.json
