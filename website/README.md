Aquí se va todo lo relacionado con la visualización de los datos y búsqueda en los mismos

## Cómo ejecutar

Define un `config.cfg` en la carpeta `config`

```
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

## Iniciar mongo

Te instalas mongo: https://docs.mongodb.com/manual/administration/install-community/
Y lo inicias según te toque


## Inserción de datos en el Mongo

Actualmente existen 2 versiones de la base de datos.

1. Contrataciones según se han extraído del portal de contrataciones de la CAM (`data.zip` en releases)
2. Backup de MongoDB DESPUÉS de haber buscado en LibreBOR la información relevante a las 200 empresas más frecuentes. (`data_librebor.zip` en releases)

La segunda versión de la base de datos nos asegura tener siempre información para un gran subset de contrataciones y además nos permite
no realizar peticiones a LibreBOR. Especialmente útil cuando no tienes una API Key o se han consumido las peticiones a la misma.

### Con data.zip

Ejecuta el script `get_data_zip.sh` dentro de la carpeta `app/models` y esto debería descargarse el zip y extraelo en la misma carpeta para generarte
todos los datos suficientes para que cuando inicies la app por primera vez se realizen todas las inserciones en MongoDB.

### Con data\_librebor.zip

Ejecuta el script `backup_mongo.sh` dentro de la carpeta `app/models` y esto debería borrarte la base de datos `dme` en casos de existir y aplicar la copia
guardada dentro de `data_librebor.zip`. No contiene los jsons originales (a diferencia de `data.zip`)
