from fastapi import FastAPI
import pandas as pd

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
