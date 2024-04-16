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