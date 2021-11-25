# Contrataciones Madrid

Bienvenido/a a Contrataciones Madrid, tu portal agregador
de contratos, listas electorales y listas de evasores fiscales favoritos.


En Contrataciones Madrid puedes encontrar 2 tipos distintos de carpetas:
- `data_gathering`: Aquí encontrarás archivos auxiliares y herramientas para obtener y generar
los datos de la misma manera que lo hemos hecho nosotros
- `website`: Aquí encontrarás la página web y todo lo necesario para ejecutarla, incluyendo los links
para que te puedas bajar los datos e inicializar el mongo igual que nosotros.


## Esto funciona gracias a...

[LibreBor](https://librebor.me/)


## Algunas estadísticas

Actualmente contamos con 137649 contratos, de los casi 3M que componen la base de datos
de la Comunidad de Madrid. ¿Porqué no tenemos todos? Para esta prueba de concepto no era necesario,
además, 137649 contratos ocupan 500MB, por lo que los 3M se podrían salir un poco de nuestro ___scope___.


De los 130K de contratos, alrededor de 100K han sido adjudicados.


De los 100K de contratos adjudicados, solo hay 6000 empresas diferentes, agrupando alguna hasta 4000 contrataciones.


Los papeles de paraísos fiscales utilizados han sido solamente los "Panama Papers", pero se pueden añadir nuevos papeles
de forma sencilla con incluir una nueva colección en el MongoDB de paraísos fiscales y los nombres de personas/empresas en la misma.
