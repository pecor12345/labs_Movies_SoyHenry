import pandas as pd
from fastapi import FastAPI 



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
        meses_nombres = {'enero': 1, 'febrero': 2, 'marzo' : 3, 'abril' : 4, 'mayo': 5, 'junio': 6,
                         'julio' : 7, 'agosto' : 8, 'septiembre' : 9, 'octubre' : 10, 'noviembre' : 11, 'diciembre' : 12}
        if mes in meses_nombres:
            mes_num = meses_nombres.index(mes) + 1
            cantidad = df_labs[df_labs['release_date'].dt.month == mes_num].shape[0]
        else:
            return {"Error. No hay información. Revise el mes ingresado por favor."}
    return {f"En el mes de ": mes, " fueron estrenadas la siguiente cantidad de peliculas:": cantidad}

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
        for _, pelicula in peliculas_del_director.iterrows():
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
        
'''@app.get("/dataframe")
def get_dataframe():
   data = df_labs
   return JSONResponse(content=data.to_json(orient='records'), media_type='application/json')

import nest_asyncio
nest_asyncio.apply()#import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)'''