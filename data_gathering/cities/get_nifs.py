from pymongo import MongoClient

mongo = MongoClient()["dme"]
contratos = mongo["contracts"]

# recupera los que tienen adjudicaciones
adjudicados = contratos.find({"adjudicacion": { "$exists" : True }})

print(f"Hay {adjudicados.count()} contratos adjudicados")

nifs = []
for contrato in adjudicados:
    try:
        nifs.append(contrato['adjudicacion']['nif adjudicatario'])
    except Exception as e:
        import pdb; pdb.set_trace()
        raise e

print(len(nifs))
