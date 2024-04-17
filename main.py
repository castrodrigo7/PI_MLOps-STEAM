from fastapi import FastAPI
from typing import List, Dict, Union
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

@app.get("/developer/{desarrollador}")
def developer(desarrollador: str):
    """
    Esta funcion calcula para un desarrolador de juego devuelve la cantidad de items y el porcentaje de contenido gratis por año
    params:
    desarrollador:str
    """
    cols_1 = ['developer', 'year', 'price']
    df = pd.read_parquet('datasets/dfgames.parquet', columns=cols_1)
    # Convertir el nombre del desarrollador a minúsculas para manejar de manera consistente las cadenas de texto
    desarrollador = desarrollador.lower()

    # Filtrar los juegos del desarrollador
    df_dev = df[df['developer'].str.lower() == desarrollador]
    
    # Calcular la cantidad de items y porcentaje de contenido Free por año
    result = []
    for year in sorted(df_dev['year'].unique(), reverse=True):  # Ordenar los años de manera descendente
        df_year = df_dev[df_dev['year'] == year]
        total_items = int(len(df_year))  # Convertir a entero estándar de Python
        free_items = int(len(df_year[df_year['price'] == 0]))  # Convertir a entero estándar de Python
        free_percentage = (free_items / total_items) * 100
        result.append({"Año": int(year), "Cantidad de Items": total_items, "Contenido Free": f"{free_percentage}%"})  # Convertir 'year' a entero estándar de Python
    
    return result

@app.get("/userdata/{user_id}")
async def userdata(user_id: str):
    # Cargar los DataFrames desde archivos parquet
    df = pd.read_parquet('datasets/dfgames.parquet')[['id', 'price']]
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')[['user_id', 'item_id', 'recommend']]
    df_items = pd.read_parquet('datasets/users_item.parquet')[['user_id', 'item_id']]
    # Filtrar las reviews del usuario
    user_reviews = df_reviews[df_reviews['user_id'] == user_id]

    # Calcular la cantidad de dinero gastado por el usuario
    user_items = df_items[df_items['user_id'] == user_id]
    user_spent = df[df['id'].isin(user_items['item_id'])]['price'].sum()

    # Calcular el porcentaje de recomendación
    recommend_pct = user_reviews['recommend'].mean() * 100

    # Calcular la cantidad de items
    item_count = user_items.shape[0]

    # Crear el diccionario de respuesta
    response = {
        "Usuario": user_id,
        "Dinero gastado": f"{user_spent} USD",
        "% de recomendación": f"{recommend_pct}%",
        "cantidad de items": item_count
    }

    return response

@app.get("/UserForGenre/{genero}")
async def UserForGenre(genero: str):
    # Cargar los DataFrames desde archivos parquet
    df = pd.read_parquet('datasets/dfgames.parquet')[['id', genero, 'year']]
    df_items = pd.read_parquet('datasets/users_item.parquet')[['user_id', 'item_id', 'playtime_forever']]

    # Filtrar los juegos del género dado
    genre_games = df[df[genero] == 1]

    # Filtrar los items de los juegos del género dado
    genre_items = df_items[df_items['item_id'].isin(genre_games['id'])]

    # Calcular las horas jugadas por usuario
    user_playtime = genre_items.groupby('user_id')['playtime_forever'].sum()

    # Encontrar el usuario con más horas jugadas
    top_user = user_playtime.idxmax()

    # Calcular la acumulación de horas jugadas por año de lanzamiento
    genre_items['year'] = genre_items['item_id'].map(genre_games.set_index('id')['year'])
    playtime_by_year = genre_items.groupby('year')['playtime_forever'].sum().reset_index()

    # Crear la lista de horas jugadas por año
    playtime_list = playtime_by_year.rename(columns={'year': 'Año', 'playtime_forever': 'Horas'}).to_dict('records')

    # Crear el diccionario de respuesta
    response = {
        f"Usuario con más horas jugadas para {genero}": top_user,
        "Horas jugadas": playtime_list
    }

    return response