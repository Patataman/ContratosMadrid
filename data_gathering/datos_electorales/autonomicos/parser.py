#!/usr/bin/env python

import urllib.request
import gzip
import shutil
import re
import json

#URLs de los datos de las elecciones en bruto
urls = ['https://github.com/franloza/infoelectoral-madrid/blob/master/files/txt/madrid_2007_candidaturas.txt.gz?raw=true' \
        , 'https://github.com/franloza/infoelectoral-madrid/blob/master/files/txt/madrid_2011_candidaturas.txt.gz?raw=true' \
        , 'https://github.com/franloza/infoelectoral-madrid/blob/master/files/txt/madrid_2015_candidaturas.txt.gz?raw=true' \
        , 'https://github.com/franloza/infoelectoral-madrid/blob/master/files/txt/madrid_2019_candidaturas%20proclamadas.txt.gz?raw=true']

filename = "autonomicas_madrid_"
ano = 2007
extension = ".txt.gz"
files = []

#Se descarga cada fichero comprimido con los datos electorales
for url in urls:
    urllib.request.urlretrieve(url, filename + str(ano) + extension)
    files.append(filename + str(ano) + extension)
    ano += 4

#Se descomprime    
for gz in files:
    with gzip.open(gz, 'rb') as f_in:
        with open(gz[0:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

listCandidaturas = []
for txt in files:
    print(txt[:-3])
    with open(txt[:-3]) as f:
        lines = f.readlines()
        partido = ""
        candidatos = []
        suplentes = []
        ano = txt[19:23]
        mode = 0
        for line in lines:
            if (line[0:1].isnumeric() == False and line != "Suplentes\n" and line != "\n"):
                if (len(candidatos) > 0):
                    #print(candidatos)
                    #print(suplentes)
                    candidatura = {
                        "ano": ano,
                        "partido": partido,
                        "candidatos": candidatos,
                        "suplentes": suplentes
                    }
                    listCandidaturas.append(candidatura)
                    
                    candidatos = []
                    suplentes = []
                
                mode = 0
                partido = re.sub("[\(\[].*?[\)\]]", "", line).rstrip("\n")
                #print(partido)
                continue
            
            if (line == "Suplentes\n"):
                mode = 1
                continue
            
            if (mode == 0):
                candidato = re.sub(r'[0-9]+', '', line)
                candidato = candidato[2:].rstrip("\n")
                candidato = re.sub("[\(\[].*?[\)\]]", "", candidato)
                if (candidato[0:4] == "Don "):
                    candidato = candidato[4:]
                if (candidato[0:5] == "Doña "):
                    candidato = candidato[5:]
                    
                if (candidato != ""):
                    if (candidato[-1] == "."):
                        candidato = candidato[:-1]
                    if (candidato[-1] == " "):
                        candidato = candidato[:-1]
                    
                    candidatos.append(candidato)
            else:
                suplente = re.sub(r'[0-9]+', '', line)
                suplente = suplente[2:].rstrip("\n")
                suplente = re.sub("[\(\[].*?[\)\]]", "", suplente)
                if (suplente[0:4] == "Don "):
                    suplente = suplente[4:]
                if (suplente[0:5] == "Doña "):
                    suplente = suplente[5:]
                    
                if (suplente != ""):
                    if (suplente[-1] == "."):
                        suplente = suplente[:-1]
                    if (suplente[-1] == " "):
                        suplente = suplente[:-1]
                    
                    suplentes.append(suplente)
            
        #print(candidatos)
        #print(suplentes)
        candidatura = {
            "ano": ano,
            "partido": partido,
            "candidatos": candidatos,
            "suplentes": suplentes
        }
        listCandidaturas.append(candidatura)
print(listCandidaturas)
with open(f"candidaturas.json", "w+") as fd:
    fd.write(json.dumps(listCandidaturas))
    fd.close()
