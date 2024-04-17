<p align=center><img src=https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Steam_2016_logo_black.svg/1280px-Steam_2016_logo_black.svg.png><p>

# <h1 align=center> **PROYECTO INDIVIDUAL Nº1** </h1>

# <h1 align=center>**`Machine Learning Operations (MLOps)`**</h1>

<p align="center">
<img src="https://user-images.githubusercontent.com/67664604/217914153-1eb00e25-ac08-4dfa-aaf8-53c09038f082.png"  height=300>
</p>

## **Introducción:**
Este proyecto consiste en crear una API que utiliza un modelo de recomendación para Steam, una plataforma multinacional de videojuegos, basado en Machine Learning. El objetivo es crear un sistema de recomendación de videojuegos para usuarios. La API ofrece una interfaz intuitiva para que los usuarios puedan obtener informacion para el sistema de recomendacion y datos sobre generos o fechas puntuales. 
Los datos utilizados incluyen información sobre juegos en la plataforma Steam y la interacción de los usuarios con estos juegos.

## ✨ **Herramientas Utilizadas**
+ Pandas
+ Matplotlib
+ Numpy
+ Seaborn
+ NLTK
+ Uvicorn
+ Render
+ FastAPI
+ Python
+ Scikit-Learn

## 💁‍♀️**Paso a paso:**

### 1. **Exploración, Transformación y Carga (ETL):**
 A partir de los 3 dataset proporcionados (steam_games, user_reviews y user_items) referentes a la plataforma de Steam, en primera instancia se realizó el proceso de limpieza de los datos. Los transformamos según las necesidades del proyecto y los cargamos en formato parquet para su análisis y uso posterior.

### 2. **Deployment de la API:**

Se desarrollaron las siguientes funciones, a las cuales se podrá acceder desde la API en la página Render:

- **`developer(desarrollador: str)`**: Retorna la cantidad de ítems y el porcentaje de contenido gratis por año para un desarrollador dado.
- **`userdata(User_id: str)`**: Retorna el dinero gastado, cantidad de ítems y el porcentaje de comentarios positivos en la revisión para un usuario dado.
- **`UserForGenre(género: str)`**: Retorna al usuario que acumula más horas para un género dado y la cantidad de horas por año.
- **`best_developer_year(año: int)`**: Retorna los tres desarrolladores con más juegos recomendados por usuarios para un año dado.
- **`developer_rec(desarrolladora: str)`**: Retorna una lista con la cantidad de usuarios con análisis de sentimiento positivo y negativo para un desarrollador dado.

### 3. **Análisis Exploratorio (EDA):** 
Teniendo los 3 dataset limpios, se realizó un proceso de EDA para realizar gráficos y así entender las estadísticas, encontrar valores atípicos y orientar un futuro análisis. Intentando asi obtener alguna pista para crear nuestro modelo de ML

### 4. **Modelo de Machine Learning:**
Realizamos un modelo de Machine Learning para generar recomendaciones juegos, utilizando algoritmos y técnicas como la similitud del coseno y scikit-lear, con el fin de brindar recomendaciones personalizadas y precisas basadas en los gustos y preferencias de cada usuario.

 Si es un sistema de recomendación item-item:
- **`def recomendacion_juego( id de producto )`**: Ingresando el id de producto ('id), deberíamos recibir una lista con 5 juegos recomendados similares al ingresado.

 Si es un sistema de recomendación user-item:
- **`def recomendacion_usuario( id de usuario )`**: Ingresando el id de un usuario ('user_id'), deberíamos recibir una lista con 5 juegos recomendados para dicho usuario.

Tambien son consultables en la API

## **`Links`**

  - [API desplegada en Render](https://steam-deploy-0v67.onrender.com/docs)
  - [Link al video](https://drive.google.com/drive/folders/1g8ejwE6h8O6D4clfkxmZuED7tfJZ_idz?usp=sharing)

