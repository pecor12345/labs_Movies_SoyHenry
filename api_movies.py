import pandas as pd
import numpy as np
import os
import ast
from datetime import datetime
from fastapi import FastAPI
from movies import Movies
from recommendation_system import Recommendation

#                                           CARGA DE DATOS

url='https://drive.google.com/file/d/1yqB8ahhhdiONfZLu8-xuU9qsWOgSf5Oo/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_labs = pd.read_csv(url)

df_labs.info()
df_labs.shape


                            #DESARROLLO Y TRANSFORMACION DE DATOS
#01.ELIMINAR COLUMNAS
df_labs.drop(columns=['video', 'imdb_id', 'adult', 'original_title', 'poster_path', 'homepage', 'tagline'], axis=1, inplace = True)

# 02.VALORES NULOS REVENUE Y BUDGET
df_labs['budget'] = pd.to_numeric(df_labs['budget'], errors='coerce').fillna(0)
df_labs['revenue'] = df_labs['revenue'].fillna(0)

#03.Crear Columna Return
df_labs['return'] = df_labs.apply(lambda x: x['revenue']/x['budget'] if x['budget'] != 0 else 0, axis=1)
df_labs.info()

#04. DESANIDAR 

#04.1 String a Diccionario
def str_to_dict(value):
    if pd.isna(value):
        return None
    else:
        return ast.literal_eval(value)
#04.2 Desanidar Columnas
df_labs['belongs_to_collection'] = df_labs['belongs_to_collection'].apply(str_to_dict)
df_nested = pd.json_normalize(df_labs['belongs_to_collection']).fillna('')
df_nested.head()

columns = df_nested.columns
new_columns_names = {column : f'belongs_to_collections_{column}' for column in columns}
df_nested.rename(columns=new_columns_names, inplace=True)
df_nested.head()
df_nested.shape

columns = ['genres', 'production_companies', 'production_countries', 'spoken_languages']

for column in columns:
    df_labs[column] = df_labs[column].apply(str_to_dict)
    df_nested = pd.json_normalize(df_labs[column]).fillna('')
    nested_columns = df_nested.columns
    df_nested_1 = pd.DataFrame()
    for nested_column in nested_columns:
        df_aux = pd.json_normalize(df_nested[nested_column]).fillna('')
        if 'production_countries' in column:
            df_aux.rename(columns={'iso_3166_1': 'id'}, inplace=True)
        if 'spoken_languages' in column:
            df_aux.rename(columns={'iso_639_1': 'id'}, inplace=True)
        df_aux.drop(columns='id', axis=1, inplace=True)
        new_columns_names = {col : f'{column}_{nested_column}_{col}' for col in df_aux.columns}
        df_aux.rename(columns=new_columns_names, inplace=True)
        df_nested_1 = pd.concat([df_nested_1, df_aux], axis=1)

# Convertir columns to a list of columns
    column_name = f'{column}_name'
    column_name_list = df_nested_1.columns.to_list()
    df_nested_1[column_name] = df_nested_1.values.tolist()
    df_nested_1.drop(columns=column_name_list, axis=1, inplace=True)
    df_labs = pd.concat([df_labs, df_nested_1], axis=1)
    df_labs.drop(columns=column, inplace=True)

df_labs.shape

#05. VALORES NULOS RELEASE_DATE
df_labs.dropna(subset=['release_date'], inplace=True)
df_labs.info()

#06. FORMATO FECHA
#06.1 CREAR COLUMNA RELEASE YEAR
regex_filter = '^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
filter = df_labs['release_date'].str.contains(regex_filter)
df_labs = df_labs[filter]
df_labs['release_year'] = df_labs['release_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date().year)

#06.2 CONVERTIR EL RELEASE DATE A FORMATO FECHA
df_labs['release_date'] = pd.to_datetime(df_labs['release_date'], format='%Y-%m-%d')
print(type(df_labs))

#                                           MODULO API


@app.get('/cantidad_filmaciones_dia/{mes}')
async def cantidad_filmaciones_mes(mes: str):
    df_combined['release_date'] = pd.to_datetime(df_combined['release_date'])
    if mes.isdigit(): 

    return {'Mes':mes, 'cantidad':filas}

@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia: str):
    df_labs['release_date'] = pd.to_datetime(df_labs['release_date'])
    fecha_filtrada = pd.to_datetime(dia)  # Fecha específica a filtrar
    df_filtrado = df_labs[df_labs['release_date'] == fecha_filtrada]
    filas = df_filtrado.loc[:]

    return {'dia':dia, 'cantidad':filas}


@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score'''
    titulo_filtrado = df_labs[df_labs['title'] ==t


films = [
    {"titulo": "Pelicula 1", "anio_estreno": 2020, "score": 8.5},
    {"titulo": "Pelicula 2", "anio_estreno": 2019, "score": 7.8},
    {"titulo": "Pelicula 3", "anio_estreno": 2021, "score": 9.2},
    # Agrega más películas aquí
]

@app.get("/peliculas/{titulo}")
def obtener_pelicula(titulo: str):
    for pelicula in films:
        if pelicula["titulo"] == titulo:
            return {
                "titulo": pelicula["titulo"],
                "anio_estreno": pelicula["anio_estreno"],
                "score": pelicula["score"]
            }
    return {"mensaje": "Pelicula no encontrada"}


    return {'titulo':titulo, 'anio':respuesta, 'popularidad':respuesta}

@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo:str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, la cantidad de votos y el valor promedio de las votaciones. 
    La misma variable deberá de contar con al menos 2000 valoraciones, 
    caso contrario, debemos contar con un mensaje avisando que no cumple esta condición y que por ende, no se devuelve ningun valor.'''
    return {'titulo':titulo, 'anio':respuesta, 'voto_total':respuesta, 'voto_promedio':respuesta}

@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor:str):
    '''Se ingresa el nombre de un actor que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno. 
    Además, la cantidad de películas que en las que ha participado y el promedio de retorno'''
    return {'actor':nombre_actor, 'cantidad_filmaciones':respuesta, 'retorno_total':respuesta, 'retorno_promedio':respuesta}

@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):
    ''' Se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno. 
    Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, retorno individual, costo y ganancia de la misma.'''
    return {'director':nombre_director, 'retorno_total_director':respuesta, 
    'peliculas':respuesta, 'anio':respuesta,, 'retorno_pelicula':respuesta, 
    'budget_pelicula':respuesta, 'revenue_pelicula':respuesta}

# ML
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    '''Ingresas un nombre de pelicula y te recomienda las similares en una lista'''
    return {'lista recomendada': respuesta}
