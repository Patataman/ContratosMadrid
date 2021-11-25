wget https://github.com/Patataman/DMyE1/releases/download/0.2.0/data_librebor.zip
unzip data_librebor.zip
echo "Deleting dme database"
mongo dme --eval "db.dropDatabase()"
echo "Indexing backup"
mongoimport --db dme --collection=contracts  data_librebor/dme_contracts.json
mongoimport --db dme --collection=company  data_librebor/dme_company.json
mongoimport --db dme --collection=electoral_list  data_librebor/dme_electoral_list.json
mongoimport --db dme --collection=offshore  data_librebor/dme_offshore.json
echo "removing .zip"
rm data_librebor.zip
