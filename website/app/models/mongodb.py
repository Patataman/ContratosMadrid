import os
import json

from pymongo import MongoClient

CONTRACTS_PATH = "app/models/data/contracts"
ELECTORAL_LISTS_PATH = "app/models/data"
CONTRACT_COLLECTION = "contracts"
ELECTORAL_LISTS_COLLECTION = "electoral_list"
DATA_BASE_ID = "dme"
MONGODB_ID = '_id'


def contract_file_to_json(file_path, file_name):
    file = open(file_path + '/' + file_name, encoding="utf8", errors='ignore')
    json_file = json.load(file)
    items = json_file.items()
    for k, v in list(items):
        if ' euros' in v or '€' in v or 'euros ' in v:
            json_file['presupuesto'] = float(json_file.pop(k).split(' ')[0].replace('.', '').replace(',', '.'))
    json_file['categoria'] = file_path.split('/')[-1]
    json_file.update({MONGODB_ID: file_name.split(".")[0]})
    file.close()
    return json_file


class MongoDB:
    def __init__(self):
        self.database = MongoClient()[DATA_BASE_ID]

    def add_contracts(self):
        if not os.path.exists(CONTRACTS_PATH):
            return
        dirs = next(os.walk(CONTRACTS_PATH))[1]
        contracts_collection = self.database[CONTRACT_COLLECTION]
        contracts_list = []
        for i in dirs:
            type_dir = CONTRACTS_PATH + '/' + i
            files = filter(lambda x: '.json' in x, next(os.walk(type_dir))[2])
            for f in files:
                if contracts_collection.find_one({MONGODB_ID: f.split('.')[0]}) is None:
                    contracts_list.append(contract_file_to_json(type_dir, f))

        contracts_collection.insert_many(contracts_list)

    def delete_all_contracts(self):
        self.database[CONTRACT_COLLECTION].drop()

    def get_all_contracts(self):
        return list(self.database[CONTRACT_COLLECTION].find({}))

    def get_contracts_by_title(self, title):
        return list(self.database[CONTRACT_COLLECTION].find({'titulo': {'$regex': ".*" + title + ".*"}}))

    def get_contract_by_id(self, id):
        return self.database[CONTRACT_COLLECTION].find_one({'_id': id})

    def get_contracts_categories(self):
        return list(self.database[CONTRACT_COLLECTION].distinct('categoria'))

    def get_contracts_by_category(self, category):
        return list(self.database[CONTRACT_COLLECTION].find({'categoria': category}))

    def add_electoral_lists(self):
        if not os.path.exists(ELECTORAL_LISTS_PATH):
            return
        files = filter(lambda x: '.json' in x, next(os.walk(ELECTORAL_LISTS_PATH))[2])
        electoral_collection = self.database[ELECTORAL_LISTS_COLLECTION]
        for i in files:
            file = open(ELECTORAL_LISTS_PATH + '/' + i, encoding="utf8", errors='ignore')
            json_file = json.load(file)
            if isinstance(json_file, list):
                electoral_collection.insert_many(json_file)
            else:
                electoral_collection.insert_one(json_file)

    def delete_all_electoral_lists(self):
        self.database[ELECTORAL_LISTS_COLLECTION].drop()

    def get_all_electoral_lists(self):
        return list(self.database[ELECTORAL_LISTS_COLLECTION].find({}))
