from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qsl

import json
import scrapy

class Contratos(scrapy.Spider):
    name = 'contratos'
    allowed_domains = ["www.madrid.org"]

    domain = 'www.madrid.org'

    start_urls = [
        # Contratos sin publicidad
        "https://www.madrid.org/cs/Satellite?c=Page&cid=1109178416227&definicion=Contratos+Publicos&idPagina=1205761917548&language=es&op=Contratos+adjudicados+por+procedimientos+sin+publicidad&pagename=PortalContratacion%2FPage%2FPCON_contratosPublicos&tipoServicio=CM_ConvocaPrestac_FA",
        # Tablon de contratos
        "https://www.madrid.org/cs/Satellite?c=Page&cid=1109178416227&definicion=Contratos+Publicos&idPagina=1203334374496&language=es&op=Tabl%C3%B3n+de+anuncio+electr%C3%B3nico&pagename=PortalContratacion%2FPage%2FPCON_contratosPublicos&tipoServicio=CM_ConvocaPrestac_FA",
    ]

    def start_requests(self):
        """ Antes del parse
        """
        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        ''' Entra dentro de cada categoría de las "start_urls"
        '''
        # El listado siempre está presente en el elemento <li> con la clase 'txt07azu' en ambas páginas
        category = response.css("li .txt07azu")
        for cat in category:
            url = cat.xpath('@href').extract_first() # URL a la página de la categoría

            yield response.follow(url, self.navigate_contract_category)

    def navigate_contract_category(self, response):
        ''' Navega por la lista de contratos en la categoría actual
        '''
        # Si no hay contrataciones, existe un elemento HTML con el id="noHay"
        noHay = response.css("#noHay").extract_first()

        if not noHay:
            # Los contratos aparecen en divs con la clase "cajaBlanca"
            contracts = response.css(".cajaBlanca")
            for contract in contracts:
                url = contract.css(".txt07azu").xpath('@href').extract_first()
                yield response.follow(url, self.contract_scrapping)

            if len(contracts) > 0:
                # Itera a la siguiente página
                parse = urlparse(response.url)
                params = dict(parse_qsl(parse.query))
                params['paginaActual'] = 2 if not 'paginaActual' in params else int(params['paginaActual'])+1
                siguientePagina = f"{parse.path}?{urlencode(params)}"

                yield response.follow(siguientePagina, self.navigate_contract_category)

    def contract_scrapping(self, response):
        ''' Scrappea la información presente en la página del contrato
        '''
        title = response.css("#titulo_cabecera h2").xpath('text()').extract_first().strip()
        status = response.css("#cont_int_izdo span").xpath("text()").extract_first().strip()

        information = response.css(".listado .txt08gr3")
        contract_details = defaultdict()
        contract_details['url'] = response.url
        contract_details['titulo'] = title
        contract_details['status'] = status
        for field in information:
            # Cuando el contrato ya ha sido adjudicado, información sobre la adjudicación
            if field.css(".tableAdjudicacion"):
                columnas = field.css(".tableAdjudicacion thead tr th[colspan='1'] span")
                valores = field.css(".tableAdjudicacion tbody tr td")
                adjudicacion = {}
                for col, val in zip(columnas, valores):
                    col_nombre = col.xpath("text()").extract_first().strip()
                    col_nombre = col_nombre.lower().replace("º", "-")
                    col_val = val.xpath("text()").extract_first()
                    if col_val:
                        col_val = col_val.strip()
                    adjudicacion[col_nombre] = col_val
            else:
                name = field.css("strong").xpath("text()").extract_first().strip()
                name_formatted = name.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ú", "u").replace("ó", "o").replace("ñ", "n")
                content = field.xpath("text()").extract_first().strip()
                contract_details[name_formatted] = content

        # https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
        params = dict(parse_qsl(urlparse(response.url).query))
        output_filename = params['cid']
        if Path(f"contracts/{contract_details['tipo-de-contrato']}/{output_filename}.json").exists():
            # No sobreescribas si ya existe
            return

        # Crea la carpeta de la categoría si no existe
        Path(f"contracts/{contract_details['tipo-de-contrato']}").mkdir(exist_ok=True,parents=True)

        with open(f"contracts/{contract_details['tipo-de-contrato']}/{output_filename}.json", "w+") as fd:
            fd.write(json.dumps(contract_details))
            fd.close()
