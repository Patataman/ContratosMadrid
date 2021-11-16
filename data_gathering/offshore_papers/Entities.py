from neo4j import GraphDatabase
import csv    

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

def print_entities(tx, country):
    with open('Entities.csv', 'w', newline='') as f:
        header = ['name']
        writer = csv.writer(f)
        writer.writerow(header)
        for record in tx.run("MATCH (n:Entity) WHERE n.country_codes CONTAINS $country RETURN DISTINCT toLower(n.name)", country = country):
            writer.writerow(record.values())
    f.close()

with driver.session() as session:
    session.read_transaction(print_entities, "ESP")

driver.close()
