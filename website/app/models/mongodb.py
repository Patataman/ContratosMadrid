from pymongo import MongoClient

import json
import os
import pymongo
import re


MONGODB_ID = '_id'
DATA_BASE_ID = "dme"

CONTRACTS_PATH = "app/models/data/contracts"
CONTRACT_COLLECTION = "contracts"
ELECTORAL_LISTS_COLLECTION = "electoral_list"
ELECTORAL_LISTS_PATH = "app/models/data/candidaturas"
OFFSHORE_COLLECTION = "offshore"
OFFSHORE_PATH = "app/models/data/offshore"
COMPANY_COLLECTION = "company"


def contract_file_to_json(file_path, file_name):
    file = open(file_path + '/' + file_name, encoding="utf8", errors='ignore')
    json_file = json.load(file)
    items = json_file.items()
    for k, v in list(items):
        if "esupuesto" in k and (' euros' in v or '€' in v or 'euros ' in v):
            # if "porte total" in v or "estimado" in v:
            v = v.split("euros")[0]
            numero = "".join([letra for i, letra in enumerate(v) if (letra == "," and v[i-1].isdigit()) or letra.isdigit()])
            numero = numero.replace(",", ".")
            json_file['presupuesto'] = float(numero)
        if k == 'adjudicacion':
            if type(v) == dict and len(v) > 0:
                vv = {kk.replace("<strong>","").replace("</strong>", ""): val for kk, val in v.items()}
                json_file[k] = vv
            else:
                # Si no es un diccionario es que está mal (o vacío), y lo quitamos
                json_file.pop(k)

    json_file['categoria'] = file_path.split('/')[-1]
    json_file.update({MONGODB_ID: file_name.split(".")[0]})
    file.close()
    return json_file

def query_format(str):
    return re.sub(
        '[aAáÁ]', '[aAáÁ]',
        re.sub('[eEéÉ]', '[eEéÉ]',
               re.sub('[iIíÍ]', '[iIíÍ]',
                      re.sub('[oOóÓ]', '[oOóÓ]',
                             re.sub('[uUúüÚÜ]', '[uUúüÚÜ]',
                                    re.sub('[nNñÑ]', '[nNñÑ]',
                                           re.sub(' +', '.*', str)
                                          )
                                   )
                            )
                     )
              )
    )

class MongoDB:
    def __init__(self):
        self.database = MongoClient()[DATA_BASE_ID]

    def init_db(self):
        """ Inicializa la bbdd si alguna colección no existe
        """
        if self.get_all_contracts().count() == 0:
            self.add_contracts()

        if self.get_all_electoral_lists().count() == 0:
            self.add_electoral_lists()

        if self.get_all_offshore_papers().count() == 0:
            self.add_offshore_papers()

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
        return self.database[CONTRACT_COLLECTION].find({})

    def get_by_contracts(self, _filter):
        return self.database[CONTRACT_COLLECTION].find(_filter)

    def get_aggregate_contracts(self, _filter):
        return self.database[CONTRACT_COLLECTION].aggregate(_filter)

    def get_contracts_by_title(self, title):
        return self.database[CONTRACT_COLLECTION].find({'titulo': {'$regex': ".*" + title + ".*", '$options': 'i'}})

    def get_contract_by_id(self, id):
        return self.database[CONTRACT_COLLECTION].find_one({'_id': id})

    def get_contracts_categories(self):
        return self.database[CONTRACT_COLLECTION].distinct('categoria')

    def get_contracts_by_category(self, category):
        return self.database[CONTRACT_COLLECTION].find({'categoria': category})

    def get_total_money(self):
        """ Query para sumar todo el dinero de los contratos
        """
        return self.database[CONTRACT_COLLECTION].aggregate(
            [
                {"$group": {"_id": '', "money": {"$sum": "$presupuesto"}}},
                {"$project": {"_id":0, "totalMoney": "$money"}}
            ]).next()['totalMoney']

    def add_electoral_lists(self):
        self.__insert_jsons(ELECTORAL_LISTS_COLLECTION, ELECTORAL_LISTS_PATH)

    def delete_all_electoral_lists(self):
        self.database[ELECTORAL_LISTS_COLLECTION].drop()

    def get_all_electoral_lists(self):
        return self.database[ELECTORAL_LISTS_COLLECTION].find({})

    def get_party_by_name(self, name):
        return self.database[ELECTORAL_LISTS_COLLECTION].find(
            {'candidatos': {'$regex': ".*" + query_format(name) + ".*", '$options': 'xsi'}},
            {'partido': 1, '_id': 0}
        )

    def add_offshore_papers(self):
        self.__insert_jsons(OFFSHORE_COLLECTION, OFFSHORE_PATH)

    def delete_offshore_papers(self):
        self.database[OFFSHORE_COLLECTION].drop()

    def get_all_offshore_papers(self):
        return self.database[OFFSHORE_COLLECTION].find({})

    def find_match_offshore(self, query_name, split="-"):
        name = query_name.split(split)
        query = [{"$unwind": "$names"}]
        for n in name:
            query.append({
                "$match": {
                    'names': {'$regex': f".*{n}.*", '$options': 'i'}
                }
            })
        return self.database[OFFSHORE_COLLECTION].aggregate(query)


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

    def update_contract(self, contract_id:int, new_data:dict):
        """ Actualiza el contrato dado
        """
        self.database[CONTRACT_COLLECTION].update_one({"_id": contract_id}, { "$set": new_data })

    def add_company(self, company:dict):
        """ Añade una nueva compañía a su colección
            Esta colección se utiliza para las localidades

            company es el diccionario que devuelve LibreBor
        """
        try:
            self.database[COMPANY_COLLECTION].insert_one(company.copy())
        except pymongo.errors.DuplicateKeyError:
            pass
        except Exception as e:
            raise e

    def get_all_companies(self):
        """ Devuelve todas las companía indexadas
        """
        return self.database[COMPANY_COLLECTION].find({})

    def add_company_dataset(self):
        """ Crea la colección de compañías a partir de los JSON
        """
        self.__insert_jsons(COMPANY_COLLECTION, COMPANY_PATH)

    def find_company(self, filters:dict):
        """ Devuelve las compañía que cumple los filtros.
            filters es un diccionario key:val
        """
        return self.database[COMPANY_COLLECTION].find(filters)

    def get_companies_locations(self):
        result = self.database[COMPANY_COLLECTION].aggregate(
            [{
                '$group' : {
                    '_id' : '$province',
                    'count' : {'$sum' : 1}
                }
            }])
        return result

    def unique_company(self):
        """ Devuelve companías únicas por NIF
        """
        # https://stackoverflow.com/questions/21053211/return-whole-document-from-aggregation
        return self.database[COMPANY_COLLECTION].aggregate([
            {
                "$group": {
                    "_id": "$nif",
                    "document": {
                        "$first": "$$CURRENT"
                    }
                }
            }
        ])
