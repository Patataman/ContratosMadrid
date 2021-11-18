import os
import json
import re

from pymongo import MongoClient

CONTRACTS_PATH = "app/models/data/contracts"
ELECTORAL_LISTS_PATH = "app/models/data/candidaturas"
OFFSHORE_PATH = "app/models/data/offshore"
CONTRACT_COLLECTION = "contracts"
ELECTORAL_LISTS_COLLECTION = "electoral_list"
OFFSHORE_COLLECTION = "offshore"
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

def query_format(str):
    return re.sub('[aAáÁ]', '[aAáÁ]', re.sub('[eEéÉ]', '[eEéÉ]', re.sub('[iIíÍ]', '[iIíÍ]', re.sub('[oOóÓ]', '[oOóÓ]', re.sub('[uUúüÚÜ]', '[uUúüÚÜ]', re.sub('[nNñÑ]', '[nNñÑ]', re.sub(' +', '.*', str)))))))

class MongoDB:
    def __init__(self):
        self.database = MongoClient()[DATA_BASE_ID]

    def add_contracts(self):
        if not os.path.exists(CONTRACTS_PATH): return
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
        return list(
            self.database[CONTRACT_COLLECTION].find({'titulo': {'$regex': ".*" + title + ".*", '$options': 'i'}}))

    def get_contract_by_id(self, id):
        return self.database[CONTRACT_COLLECTION].find_one({'_id': id})

    def get_contracts_categories(self):
        return list(self.database[CONTRACT_COLLECTION].distinct('categoria'))

    def get_contracts_by_category(self, category):
        return list(self.database[CONTRACT_COLLECTION].find({'categoria': category}))

    def add_electoral_lists(self):
        self.__insert_jsons(ELECTORAL_LISTS_COLLECTION, ELECTORAL_LISTS_PATH)

    def delete_all_electoral_lists(self):
        self.database[ELECTORAL_LISTS_COLLECTION].drop()

    def get_all_electoral_lists(self):
        return list(self.database[ELECTORAL_LISTS_COLLECTION].find({}))

    def get_party_by_name(self, name):
        return list(self.database[ELECTORAL_LISTS_COLLECTION].find(
            {'candidatos': {'$regex': ".*" + query_format(name) + ".*", '$options': 'xsi'}}, {'partido': 1, '_id': 0}))

    def add_offshore_papers(self):
        self.__insert_jsons(OFFSHORE_COLLECTION, OFFSHORE_PATH)

    def delete_offshore_papers(self):
        self.database[OFFSHORE_COLLECTION].drop()

    def get_all_offshore_papers(self):
        return list(self.database[OFFSHORE_COLLECTION].find({}))

    def __insert_jsons(self, collection, path):
        if not os.path.exists(path): return
        files = filter(lambda x: '.json' in x, next(os.walk(path))[2])
        collection = self.database[collection]
        for i in files:
            file = open(path + '/' + i, encoding="utf8", errors='ignore')
            json_file = json.load(file)
            if isinstance(json_file, list):
                collection.insert_many(json_file)
            else:
                collection.insert_one(json_file)

