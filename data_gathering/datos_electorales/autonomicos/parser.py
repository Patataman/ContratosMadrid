#!/usr/bin/env python

import urllib.request
import gzip
import shutil
import re

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
            
with open('autonomicas_madrid_2007.txt') as f:
    lines = f.readlines()
    listPartidos = []
    partido = ""
    candidatos = []
    suplentes = []
    mode = 0
    count = 0
    for line in lines:
        if (line[0:1].isnumeric() == False and line != "Suplentes\n" and line != "\n"):
            if (len(candidatos) > 0):
                print(candidatos)
                print(suplentes)
                candidatos = []
                suplentes = []
            
            mode = 0
            partido = line
            print(line)
            count += 1
            continue
        
        if (line == "Suplentes\n"):
            mode = 1
            count += 1
            continue
        
        if (mode == 0):
            candidato = re.sub(r'[0-9]+', '', line)
            candidato = candidato[2:].rstrip("\n")
            if (candidato != ""):
                if (candidato[-1] == "."):
                    candidato = candidato[:-1]
                
                candidatos.append(candidato)
        else:
            suplente = re.sub(r'[0-9]+', '', line)
            suplente = suplente[2:].rstrip("\n")
            if (suplente != ""):
                if (suplente[-1] == "."):
                    suplente = suplente[:-1]
                
                suplentes.append(suplente)
        
        count += 1
        #print(f'line {count}: {line}')
    print(candidatos)
    print(suplentes)
