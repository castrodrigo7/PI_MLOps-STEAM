from fastapi import FastAPI
import pandas as pd
import gzip

app = FastAPI()

# Cargar los datos


df = pd.read_csv('datasets/dfgames.csv')
df_reviews = pd.read_csv('datasets/user_reviews.csv')
# Utiliza gzip para abrir el archivo comprimido y pandas para leer el CSV
with gzip.open('datasets/users_item.csv.gz', 'rt', encoding='utf-8') as f:
# Lee el archivo CSV directamente desde el archivo comprimido
    df_items = pd.read_csv(f)

# Esta función devuelve la cantidad de items y el porcentaje de contenido gratuito por año según el desarrollador
@app.get('/developer/{desarrollador}')
def developer(desarrollador: str):
    # Filtrar datos para el desarrollador específico
    datos_desarrollador = df[df['developer'] == desarrollador]

    # Agrupar por año y calcular la cantidad de items y el porcentaje de contenido gratuito
    resumen_por_año = datos_desarrollador.groupby('year').agg(
        cantidad_items=('id', 'count'),
        contenido_free=('price', lambda x: (x == 'Free To Play').sum() / len(x) * 100)
    ).reset_index()

    # Convertir el resultado a un diccionario
    resultado_dict = resumen_por_año.to_dict(orient='records')

    return resultado_dict

# Función para obtener la información del usuario
@app.get('/userdata/{user_id}')
def userdata(user_id: str):
    # Filtrar datos para el usuario específico en los DataFrames
    user_data_games = df[df['id'] == user_id]
    user_data_reviews = df_reviews[df_reviews['user_id'] == user_id]
    user_data_item = df_items[df_items['user_id'] == user_id]

    # Calcular la cantidad de dinero gastado
    dinero_gastado = user_data_games['price'].sum()

    # Calcular el porcentaje de recomendación en base a reviews.recommend
    porcentaje_recomendacion = (user_data_reviews['recommend'].sum() / len(user_data_reviews)) * 100

    # Obtener la cantidad de items
    cantidad_items = user_data_item['item_id'].nunique()

    # Crear un diccionario con la información
    user_info_dict = {
        'Usuario': user_id,
        'Dinero gastado': f'{dinero_gastado:.2f} USD',
        'Porcentaje de recomendación': f'{porcentaje_recomendacion:.2f}%',
        'Cantidad de items': cantidad_items
    }

    return user_info_dict
    
   # Función para obtener el usuario con más horas jugadas para un género y la acumulación de horas por año
@app.get('/user_for_genre/{genero}')
def UserForGenre(genero: str):

    # Filtrar datos para el género específico en el DataFrame 
    genre_data = df[df[genero] == 1]

    if genre_data.empty:
        return print(f"No se encontraron datos para el género: {genero}")

    # Combinar datos usando 'id' y 'item_id' como claves respectivas
    combined_data = pd.merge(df_items, genre_data, left_on='item_id', right_on='id', how='inner')

    # Encontrar el usuario con más horas jugadas para el género
    usuario_mas_horas = combined_data.loc[combined_data['playtime_forever'].idxmax()]['user_id']

    # Calcular la acumulación de horas jugadas por año
    acumulacion_horas = combined_data.groupby('year')['playtime_forever'].sum().reset_index()
    acumulacion_horas = acumulacion_horas.rename(columns={'year': 'Año','playtime_forever': 'Horas'})

    # Crear un diccionario con la información
    resultado = {
        'Usuario con más horas jugadas para género': usuario_mas_horas,
        'Horas jugadas': acumulacion_horas.to_dict(orient='records')
    }

    return resultado
    
    # Función para obtener el top 3 de desarrolladores con juegos más recomendados por usuarios para el año dado
@app.get('/best_developer_year/{year}', response_model=list[dict], summary="Obtener el top 3 de desarrolladores para un año dado")
def best_developer_year(year: int):
    # Comprobar la existencia del año en los datos
    if year not in df['year'].values:
        return print(f"No hay datos disponibles para el año {year}")

    # Filtrar juegos por año
    games_year = df[df['year'] == year]

    # Filtrar por reviews positivas
    positive_reviews = df_reviews[df_reviews['sentiment_analysis'] == 2]

    # Unir juegos y reviews
    merged_data = pd.merge(positive_reviews, games_year, left_on='item_id', right_on='id')

    # Contar las recomendaciones por desarrollador
    developer_recommendations = merged_data['developer'].value_counts().reset_index()
    developer_recommendations.columns = ['Developer', 'Recommendations']

    # Obtener el top 3 de desarrolladores
    top_developers = developer_recommendations.head(3).to_dict(orient='records')

    # Formatear la respuesta
    result = [{"Puesto {}: {}".format(idx + 1, developer['Developer']): developer['Recommendations']} for idx, developer in enumerate(top_developers)]

    return result
    
@app.get('/developer_reviews_analysis/{developer}', response_model=dict, summary="Análisis de reseñas por desarrollador")
def developer_reviews_analysis(developer: str):

    print(f"Parámetro 'developer' recibido: {developer}")
        
    # Filtrar reseñas por desarrollador
    developer_reviews = df[df['developer'] == developer]

    # Verificar si el desarrollador tiene reseñas
    if developer_reviews.empty:
        return {developer: {"Negative": 0, "Positive": 0}}
    
    merged_data = pd.merge(df_reviews, developer_reviews, left_on='item_id', right_on='id')

    # Contar la cantidad de reseñas positivas y negativas
    sentiment_counts = merged_data['sentiment_analysis'].value_counts()

    # Crear el diccionario de resultados en el formato deseado
    result = {developer: {"Negative": int(sentiment_counts.get(1, 0)), "Positive": int(sentiment_counts.get(2, 0))}}

    return result

    