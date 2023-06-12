from fastapi import FastAPI 
import pandas as pd 
import uvicorn 
import os
import sys
import time
import json
import requests
import urllib3
import logging
import argparse
import traceback
import re
import random
import string
import datetime
import threading
import queue
import concurrent.futures
import urllib.parse
import urllib.request
import urllib.error
#                                           MODULO API
app = FastAPI()

url='https://drive.google.com/file/d/1yqB8ahhhdiONfZLu8-xuU9qsWOgSf5Oo/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_labs = pd.read_csv(url)

# Función 01 : CANTIDAD DE FILMACIONES POR MES
@app.get("/cantidad_filmaciones_mes/{mes}")
async def cantidad_filmaciones_mes(mes: str):
    df_labs['release_date'] = pd.to_datetime(df_labs['release_date'])
    if mes.isdigit():
        mes_num = int(mes)
        cantidad = df_labs[df_labs['release_date'].dt.month == mes_num].shape[0]
    else:
        mes = mes.lower()
        meses_nombres = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                         'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        if mes in meses_nombres:
            mes_num = meses_nombres.index(mes) + 1
            cantidad = df_labs[df_labs['release_date'].dt.month == mes_num].shape[0]
        else:
            return {"Error. No hay información. Revise el mes ingresado por favor."}
    return {"En el mes de ": mes, " fueron estrenadas la siguiente cantidad de peliculas:": cantidad}

#Función 02: CANTIDAD DE FILMACIONES POR DÍA
@app.get("/cantidad_filmaciones_dia/{dia}")
async def cantidad_filmaciones_dia(dia: str):
    if dia.isdigit():
        dia_num = int(dia)
    else:
        dia = dia.lower()
        dias_nombres = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        if dia in dias_nombres:
            dia_num = dias_nombres.index(dia) + 1
        else:
            return {"Error. El día ingresado no es válido. Ingrese nuevamente el día."}
        
    cantidad = df_labs[df_labs['release_date'].dt.day == dia].shape[0]
    cantidad = df_labs[df_labs['release_date'].dt.day == dia_num].shape[0]

    return {"En el dia ": dia, "se estrenaron la siguiente cantidad de películas:": cantidad}

#Función 03: PELICULA DONDE SE INCLUYE AÑO DE ESTRENO Y PUNTAJE
@app.get("/titulo_de_la_filmacion/{titulo}")
async def titulo_de_la_filmacion(titulo: str):
    titulo = titulo.lower()
    peliculas = df_labs[df_labs['title'].str.lower().str.contains(titulo)]
    if peliculas.shape[0] == 0:
        return {"Error. No hay informacion para esta película, por favor revise el Titulo e intentelo nuevamente."}
    else:
        pelicula = peliculas.iloc[0]
    
        devolucion = {
        "Pelicula": peliculas.iloc[0]['title'], 
        "Año de estreno": str(peliculas.iloc[0]['release_year']),
        "Valoración": str(peliculas.iloc[0]['vote_average'])
        }
    return devolucion

#Función 04: PELICULA DONDE SE INCLUYE NOMBRE, CANTIDAD DE VOTOS Y PROMEDIO DE VALORACIÓN
@app.get("/votos_titulo/{votos}")
async def votos_titulo(votos: str):
    titulo = titulo.lower()
    peliculas = df_labs[df_labs['title'].str.lower() == titulo]
    if peliculas.empty:
        return {"Error, Titulo no cuenta con la información solicitada"}
    else:
        pelicula = peliculas.iloc[0]
        if pelicula['vote_count'] < 2000:
            return {f"Error. La película {titulo} no tiene suficientes votos"}
        else:
            devolucion = {
                "titulo": str(pelicula['title']),
                "anio": str(pelicula['release_year']),
                "voto_total": str(pelicula['vote_count']),
                "voto_promedio": str(pelicula['vote_average'])
            }
            return devolucion

#Función 05: ACTOR Y SUS PARTICIPACIONES
@app.get("/nombre_actor/{actor}")
async def nombre_actor(actor: str):
    actor = actor.lower()
    actores = df_labs[df_labs['cast'].str.lower().str.contains(actor)]

    if actores.shape[0] == 0:
        return {"Error. No hay informacion para este actor, por favor revise el nombre e intentelo nuevamente."}
    else:
        actor = actores.iloc[0]
        cantidad_peliculas = actores.shape[0]
        retorno_promedio = actores / cantidad_peliculas if cantidad_peliculas > 0 else 0

        devolucion = {
            "Actor : ": actor['cast'], 
            "Participaciones: ": actor['num_critic_for_reviews'],
            "Promedio participaciones: ": retorno_promedio
        }

        return devolucion
   
 #Función 06: DIRECTOR Y SUS EXITOS
@app.get("/nombre_director/{director}")
async def nombre_director(director: str):
    director = director.lower()
    df_labs['crew'] = df_labs['crew'].str.lower()
    peliculas_del_director = df_labs[df_labs['crew'].str.contains(director, na=False)]

    if peliculas_del_director.shape[0] == 0:
        return {"Error. Director no encontrado"}
    else:
        resultados = []
        for _, pelicula in peliculas_del_directo.iterrows():
            resultados.append({
                "titulo": str(pelicula['title']),
                "anio": str(pelicula['release_year']),
                "retorno_pelicula": str(pelicula['return']),
                "budget_pelicula": str(pelicula['budget']),
                "revenue_pelicula": str(pelicula['revenue'])
            })
        retorno_total = peliculas_del_director['return'].sum()

        return {
            "director": director,
            "retorno_total_director": str(retorno_total),
            "peliculas": resultados
            }
    
#importar funciones
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer 

#Limpiar datos, crear caracteristicas y combinar colunmas
df_labs['genres'] = df_labs['genres'].fillna('')
df_labs['features'] = df_labs['genres'].astype(str) + ' ' + df_labs['vote_average'].astype(str)

# Crear a TF-IDF matrix para caracteristicas combinadas
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df_combined['features'])

#Definiendo la función de Recomendación
def recomendacion(titulo):
    titulo = titulo.lower()
    pelicula_seleccionada = df_labs[df_labs['title'].str.lower() == titulo]

    if pelicula_seleccionada.empty:
        return []

 #Filtrar peliculas por titulo   
    index = pelicula_seleccionada.index[0]
#Obtener el ID de la pelicula seleccionada
    id_pelicula_seleccionada = pelicula_seleccionada.iloc
# calcular la similitud entre peliculas 
    similarity_scores = cosine_similarity(tfidf_matrix[index], tfidf_matrix)
# Ranking de peliculas parecidas
    similar_movies_indices = similarity_scores.argsort()[0][::-1]
    similar_movies_indices = similar_movies_indices[similar_movies_indices != index]
    peliculas_similares = df_combined.iloc[similar_movies_indices][:5][['title', 'vote_average']].values.tolist()
#Peliculas con alta valoración
    peliculas_similares = sorted(peliculas_similares, key=lambda x: x[1], reverse=True)
    while len(peliculas_similares) < 5:
        peliculas_similares.append(['Película adicional', 0])

    return peliculas_similares

 #Crear una función para recomendar películas
@app.get("/recomendacion/{titulo}")
async def obtener_recomendacion(titulo: str):
    recomendaciones = recomendacion(titulo)
    if len(recomendaciones) == 0:
        return {"Error": "Película no encontrada"}
    else:
        return {"lista_recomendada": recomendaciones}



    


                         
                         
           
                      
        

            
                        

        
                
    