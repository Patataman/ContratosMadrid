from neo4j import GraphDatabase
import csv    

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

def print_intermediaries(tx, country):
    with open('Intermediaries.csv', 'w', newline='') as f:
        header = ['name']
        writer = csv.writer(f)
        writer.writerow(header)
        for record in tx.run("MATCH (n:Intermediary) WHERE n.country_codes CONTAINS $country RETURN n.name", country = country):  
            writer.writerow(record.values())
    f.close()

with driver.session() as session:
    session.read_transaction(print_intermediaries, "ESP")

driver.close()