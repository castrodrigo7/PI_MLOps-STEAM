from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

@app.get("/playtime_genre/{genero}")
def play_time_genre(genero: str):
    # Cargar los datos dentro de la función
    cols_1 = ['id', genero, 'year']
    df = pd.read_parquet('datasets/dfgames.parquet', columns=cols_1)
    cols_2 = ['item_id', 'playtime_forever']
    df_items = pd.read_parquet('datasets/users_item.parquet', columns=cols_2)

    # Verifica si el género especificado es una columna en el DataFrame
    if genero not in df.columns:
        return {"error": "El género especificado no existe en los datos"}

    # Filtra el DataFrame por el género especificado
    df_genre = df[df[genero] == 1]

    # Si df_genre está vacío, devuelve un mensaje de error
    if df_genre.empty:
        return {"error": "No hay juegos del género especificado en los datos"}

    # Une df_genre con df_items en la columna 'id'/'item_id'
    df_merged = pd.merge(df_genre, df_items, left_on='id', right_on='item_id')

    # Si df_merged está vacío, devuelve un mensaje de error
    if df_merged.empty:
        return {"error": "No hay juegos del género especificado en los datos de los items"}

    # Agrupa por año y suma las horas jugadas, luego obtén el año con el máximo total
    year_max_playtime = df_merged.groupby('year')['playtime_forever'].sum().idxmax()

    return {"Año de lanzamiento con más horas jugadas para el género {0}".format(genero) : int(year_max_playtime)}

@app.get('/user_for_genre/{genero}')
def UserForGenre(genero: str):
    # Cargar los datos dentro de la función
    cols_1 = ['id', genero, 'year']
    df = pd.read_parquet('datasets/dfgames.parquet', columns=cols_1)
    cols_2 = ['user_id', 'item_id', 'playtime_forever']
    df_items = pd.read_parquet('datasets/users_item.parquet', columns=cols_2)
    # Verifica si el género especificado es una columna en el DataFrame
    if genero not in df.columns:
        return {"error": "El género especificado no existe en los datos"}

    # Filtra el DataFrame por el género especificado
    df_genre = df[df[genero] == 1]

    # Une df_genre con df_items en la columna 'id'/'item_id'
    df_merged = pd.merge(df_genre, df_items, left_on='id', right_on='item_id')

    # Agrupa por usuario y suma las horas jugadas
    user_playtime = df_merged.groupby('user_id')['playtime_forever'].sum()

    # Encuentra el usuario con más horas jugadas
    max_playtime_user = user_playtime.idxmax()

    # Agrupa por año y suma las horas jugadas
    year_playtime = df_merged.groupby('year')['playtime_forever'].sum()

    # Convierte year_playtime a una lista de diccionarios
    playtime_list = [{"Año": year, "Horas": playtime} for year, playtime in year_playtime.items()]

    return {"Usuario con más horas jugadas para el género {0}".format(genero): max_playtime_user, "Horas jugadas": playtime_list}

@app.get("/UsersRecommend/{year}")
async def UsersRecommend(year: int):
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')
    # Filtrar las reseñas por año y recomendación
    df_filtered = df_reviews[(df_reviews['posted year'] == year) & (df_reviews['recommend'] == True) & (df_reviews['sentiment_analysis'] >= 1)]
    
    # Agrupar por item_id y contar las reseñas
    df_grouped = df_filtered.groupby('item_id').size().reset_index(name='counts')
    
    # Ordenar por conteo y tomar el top 3
    df_sorted = df_grouped.sort_values(by='counts', ascending=False).head(3)
    
    # Restablecer el índice
    df_sorted = df_sorted.reset_index(drop=True)
    
    # Crear la lista de resultados
    results = [{"Puesto {}".format(i+1): row['item_id']} for i, row in df_sorted.iterrows()]
    
    return results

@app.get("/UsersWorstDeveloper/{year}")
async def UsersWorstDeveloper(year: int):
    df = pd.read_parquet('datasets/dfgames.parquet')
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')
    # Filtrar las reseñas por año y recomendación
    df_filtered = df_reviews[(df_reviews['posted year'] == year) & (df_reviews['recommend'] == False) & (df_reviews['sentiment_analysis'] == 0)]
    
    # Unir con el DataFrame de juegos para obtener los nombres de los desarrolladores
    df_joined = df_filtered.merge(df, left_on='item_id', right_on='id')
    
    # Agrupar por desarrollador y contar las reseñas
    df_grouped = df_joined.groupby('developer').size().reset_index(name='counts')
    
    # Ordenar por conteo y tomar el top 3
    df_sorted = df_grouped.sort_values(by='counts', ascending=True).head(3)
    
    # Restablecer el índice
    df_sorted = df_sorted.reset_index(drop=True)
    
    # Crear la lista de resultados
    results = [{"Puesto {}".format(i+1): row['developer']} for i, row in df_sorted.iterrows()]
    
    return results

@app.get("/sentiment_analysis/{developer}")
async def sentiment_analysis(developer: str):
    df = pd.read_parquet('datasets/dfgames.parquet')
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')
    # Unir con el DataFrame de juegos para obtener los nombres de los desarrolladores
    df_joined = df_reviews.merge(df, left_on='item_id', right_on='id')
    
    # Filtrar las reseñas por desarrollador
    df_filtered = df_joined[df_joined['developer'] == developer]
    
    # Contar las reseñas por análisis de sentimiento
    sentiment_counts = df_filtered['sentiment_analysis'].value_counts().to_dict()
    
    # Crear el diccionario de resultados
    results = {developer: [{'Negative': sentiment_counts.get(0, 0)}, {'Neutral': sentiment_counts.get(1, 0)}, {'Positive': sentiment_counts.get(2, 0)}]}
    
    return results

@app.get("/recomendacion_juego/{item_id}")
async def recomendacion_juego(item_id: int):
    df = pd.read_parquet('datasets/dfgames.parquet')
    # Calcular la matriz de similitud del coseno
    similarity_matrix = cosine_similarity(df)
    
    # Obtener los índices de los 5 juegos más similares
    similar_items = similarity_matrix[item_id].argsort()[-6:-1][::-1]
    
    # Crear la lista de resultados
    results = [{"Juego {}".format(i+1): df.iloc[item]['app_name']} for i, item in enumerate(similar_items)]
    
    return results

@app.get("/recomendacion_usuario/{user_id}")
async def recomendacion_usuario(user_id: str):
    df = pd.read_parquet('datasets/dfgames.parquet')
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')
    # Filtrar las reseñas por usuario
    user_reviews = df_reviews[df_reviews['user_id'] == user_id]
    
    # Encontrar usuarios similares
    similar_users = df_reviews[df_reviews['item_id'].isin(user_reviews['item_id']) & (df_reviews['user_id'] != user_id)]
    
    # Recomendar juegos que a los usuarios similares les gustaron
    recommended_items = similar_users['item_id'].value_counts().index[:5]
    
    # Crear la lista de resultados
    results = [{"Juego {}".format(i+1): df[df['id'] == item]['app_name'].values[0]} for i, item in enumerate(recommended_items)]
    
    return results