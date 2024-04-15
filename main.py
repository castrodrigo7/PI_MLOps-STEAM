from fastapi import FastAPI
import pandas as pd
import gzip


app = FastAPI()

# Cargar los datos
df = pd.read_csv('datasets/dfgames.csv')
df_reviews = pd.read_csv('datasets/user_reviews.csv')
df_items = pd.read_parquet('datasets/users_item.parquet')

""" # Definir la función para leer el archivo CSV comprimido línea por línea
def read_gzip_csv(filename):
    data = []
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        # Leer cada línea del archivo CSV y convertirla en un DataFrame
        for line in f:
            # Dividir la línea en columnas usando la coma como delimitador
            row = line.strip().split(',')
            data.append(row)
    # Crear un DataFrame a partir de los datos recopilados
    df = pd.DataFrame(data[1:], columns=data[0])
    return df """

""" # Utilizar la función para leer el archivo CSV comprimido
df_items = read_gzip_csv('datasets/users_item.csv.gz') """
# df_items = pd.read_csv('datasets/user_item.csv')


@app.get("/playtime_genre/{genero}")
def play_time_genre(genero: str):
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
    # Cargar los datos solo cuando sea necesario
    df = pd.read_csv('datasets/dfgames.csv')
    df_items = pd.read_parquet('datasets/users_item.parquet')
    
    # Convertir el género ingresado por el usuario a minúsculas
    genero = genero.lower()

    # Filtrar datos para el género específico en el DataFrame 
    genre_data = df[df[genero] == 1]

    if genre_data.empty:
        return {"message": f"No se encontraron datos para el género: {genero}"}

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

# Función para obtener el top 3 de juegos más recomendados por usuarios para un año dado
def get_top_3_recommended_games(year: int):
    # Fusionar los DataFrames df_reviews y df con las columnas relevantes
    merged_df = pd.merge(df_reviews, df[['app_name', 'year']], left_on='item_id', right_on='id', how='inner')

    # Filtrar por el año especificado y las recomendaciones positivas/neutrales
    filtered_df = merged_df[(merged_df['year'] == year) & (merged_df['recommend'] == True) & (merged_df['sentiment_analysis'] != 0)]

    # Contar el número de recomendaciones para cada juego
    game_counts = filtered_df['app_name'].value_counts()

    # Obtener los top 3 juegos más recomendados
    top_3_games = game_counts.head(3).reset_index().to_dict(orient='records')

    # Formatear el resultado según el ejemplo de retorno
    formatted_result = [{"Puesto " + str(i+1): game} for i, game in enumerate(top_3_games)]

    return formatted_result

# Endpoint para obtener el top 3 de juegos más recomendados por usuarios para un año dado
@app.get('/UsersRecommend/{año}')
async def UsersRecommend(año: int):
    return get_top_3_recommended_games(año)

@app.get('/best_developer_year/{year}', response_model=list[dict], summary="Obtener el top 3 de desarrolladores para un año dado")
def best_developer_year(year: int):

    # Convertir el año ingresado por el usuario a un entero
    year = int(year)

    # Comprobar la existencia del año en los datos
    if year not in df['year'].values:
        return {"message": f"No hay datos disponibles para el año {year}"}

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
    # Cargar los datos solo cuando sea necesario
    df = pd.read_csv('datasets/dfgames.csv')
    df_reviews = pd.read_csv('datasets/user_reviews.csv')

    # Convertir el desarrollador ingresado por el usuario a minúsculas
    developer = developer.lower()

    print(f"Parámetro 'developer' recibido: {developer}")
        
    # Filtrar reseñas por desarrollador
    developer_reviews = df[df['developer'].str.lower() == developer]

    # Verificar si el desarrollador tiene reseñas
    if developer_reviews.empty:
        return {developer: {"Negative": 0, "Positive": 0}}
    
    merged_data = pd.merge(df_reviews, developer_reviews, left_on='item_id', right_on='id')

    # Contar la cantidad de reseñas positivas y negativas
    sentiment_counts = merged_data['sentiment_analysis'].value_counts()

    # Crear el diccionario de resultados en el formato deseado
    result = {developer: {"Negative": int(sentiment_counts.get(1, 0)), "Positive": int(sentiment_counts.get(2, 0))}}

    return result
