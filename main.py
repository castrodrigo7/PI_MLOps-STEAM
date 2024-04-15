from fastapi import FastAPI
import pandas as pd


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
