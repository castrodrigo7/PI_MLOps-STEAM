from fastapi import FastAPI
from typing import List, Dict, Union
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

app = FastAPI()


@app.get("/developer/{desarrollador}")
def developer(desarrollador: str):

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
    genre_items['year'] = genre_items['item_id'].map(genre_games.set_index('id')['year'].to_dict())
    playtime_by_year = genre_items.groupby('year')['playtime_forever'].sum().reset_index()

    # Crear la lista de horas jugadas por año
    playtime_list = playtime_by_year.rename(columns={'year': 'Año', 'playtime_forever': 'Horas'}).to_dict('records')

    # Crear el diccionario de respuesta
    response = {
        f"Usuario con más horas jugadas para {genero}": top_user,
        "Horas jugadas": playtime_list
    }

    return response


@app.get("/best_developer_year/{year}")
async def best_developer_year(year: int):
    # Cargar los DataFrames desde archivos CSV
    df = pd.read_parquet('datasets/dfgames.parquet')[['id', 'developer', 'year']]
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')[['item_id', 'recommend']]

    # Convertir el año a int
    df['year'] = df['year'].astype(int)

    # Filtrar los juegos del año dado
    year_games = df[df['year'] == year].copy()  # Crear una copia explícita del DataFrame

    # Filtrar las reviews de los juegos del año dado que fueron recomendados
    recommended_reviews = df_reviews[(df_reviews['item_id'].isin(year_games['id'])) & (df_reviews['recommend'] == True)]

    # Calcular la cantidad de recomendaciones por juego
    game_recommendations = recommended_reviews['item_id'].value_counts()

    # Asignar la cantidad de recomendaciones a cada juego
    year_games.loc[:, 'recommendations'] = year_games['id'].map(game_recommendations)

    # Calcular la cantidad de recomendaciones por desarrollador
    developer_recommendations = year_games.groupby('developer')['recommendations'].sum()

    # Verificar si no hay desarrolladores con recomendaciones
    if developer_recommendations.empty:
        return "No se encontraron desarrolladores con recomendaciones para ese año."

    # Encontrar el top 3 de desarrolladores
    top_developers = developer_recommendations.nlargest(3)

    # Crear la lista de desarrolladores
    developer_list = [{"Puesto " + str(i+1): developer} for i, developer in enumerate(top_developers.index)]

    return developer_list


@app.get("/developer_reviews_analysis/{desarrolladora}")
async def developer_reviews_analysis(desarrolladora: str):

    # Cargar los DataFrames desde archivos parquet una sola vez al inicio
    df_reviews = pd.read_parquet('datasets/user_reviews.parquet')[['item_id', 'recommend', 'sentiment_analysis']]
    df_games = pd.read_parquet('datasets/dfgames.parquet')[['id', 'developer']]

    # Convertir todos los nombres de los desarrolladores en letras minúsculas para evitar la duplicación de datos debido a las diferencias de mayúsculas y minúsculas
    df_games['developer'] = df_games['developer'].str.lower()

    # Convertir el nombre del desarrollador proporcionado en letras minúsculas
    desarrolladora = desarrolladora.lower()

    # Filtrar por desarrollador y realizar el merge con las reseñas
    developer_data = pd.merge(df_reviews,df_games[df_games['developer'] == desarrolladora],left_on='item_id',right_on='id',how='inner')

    # Verificar si se encuentra los juegos del desarrollador en el dataset
    if developer_data.empty:
        return 'No se encontraron reviews para ese desarrollador'

    # Contar los sentimientos de análisis de comentarios
    sentiment_counts = developer_data['sentiment_analysis'].value_counts()

    # Devolver conteos en un diccionario
    return {desarrolladora: {'Negative': int(sentiment_counts.get(0, 0)),'Positive': int(sentiment_counts.get(2, 0))}}




@app.get("/recommendation/{item_id}")
async def recommend(item_id: str):

    # Cargar los DataFrames desde archivos parquet
    df = pd.read_parquet('datasets/dfgames.parquet')[['app_name', 'id']].sample(n=20000)
    df_items = pd.read_parquet('datasets/users_item.parquet')[['user_id', 'item_id', 'playtime_forever']].sample(n=20000)

    # Unir los dataframes para obtener los nombres de los juegos
    df_items = df_items.merge(df, left_on='item_id', right_on='id')

    # Eliminar entradas duplicadas
    df_items = df_items.drop_duplicates(subset=['user_id', 'item_id'])

    # Crear una matriz de calificaciones de usuario-ítem
    df_items['user_id'] = df_items['user_id'].astype('category')
    df_items['item_id'] = df_items['item_id'].astype('category')

    ratings = csr_matrix((df_items['playtime_forever'], 
                        (df_items['item_id'].cat.codes, df_items['user_id'].cat.codes)))

    # Calcular la matriz de similitud del coseno con los datos reducidos
    cosine_sim = cosine_similarity(ratings, dense_output=False)

    # Crear un mapa inverso de índices y nombres de juegos
    indices = pd.Series(df.index, index=df['app_name']).drop_duplicates()

    # Obtener el índice del juego que coincide con el título
    idx = indices[int(item_id)]

    # Obtener las puntuaciones de similitud por pares de todos los juegos con ese juego
    sim_scores = list(enumerate(cosine_sim[idx].toarray()[0]))

    # Ordenar los juegos en función de las puntuaciones de similitud
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obtener las puntuaciones de los 5 juegos más similares
    sim_scores = sim_scores[1:6]

    # Obtener los índices de los juegos
    game_indices = [i[0] for i in sim_scores]

    # Devolver los 5 juegos más similares
    recommended_games = df['app_name'].iloc[game_indices].tolist()

    return {"Recommended Games": recommended_games}
