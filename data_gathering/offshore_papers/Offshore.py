from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

def print_officers(tx, country):
    data = set()
    for record in tx.run("MATCH (n:Officer) WHERE n.country_codes CONTAINS $country RETURN DISTINCT toLower(n.name)", country = country):
        data.add(record.values()[0])
    for record in tx.run("MATCH (n:Intermediary) WHERE n.country_codes CONTAINS $country RETURN DISTINCT toLower(n.name)", country = country):
        data.add(record.values()[0])
    for record in tx.run("MATCH (n:Entity) WHERE n.country_codes CONTAINS $country RETURN DISTINCT toLower(n.name)", country = country):
        data.add(record.values()[0])
    offshore = {"names": list(data)}
    with open('offshore_papers.json', 'w') as outfile:
        json.dump(offshore, outfile)

with driver.session() as session:
    session.read_transaction(print_officers, "ESP")

driver.close()
