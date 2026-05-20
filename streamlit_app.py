# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Mostrar opciones de frutas con la nueva columna SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Ver el contenido del DataFrame para confirmar
st.dataframe(data=my_dataframe, use_container_width=True)

# Pausar ejecución para revisar esta parte (puedes quitarlo después)
st.stop()

# Selección de ingredientes usando FRUIT_NAME
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Mostrar subtítulo con el nombre de la fruta
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Usar SEARCH_ON para la llamada a la API
        search_value = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).to_pandas()['SEARCH_ON'].iloc[0]
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_value.lower())

        # Mostrar los datos nutricionales
        sf_df = pd.DataFrame([smoothiefroot_response.json()])
        st.dataframe(sf_df, use_container_width=True)

    # Botón para insertar el pedido
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
