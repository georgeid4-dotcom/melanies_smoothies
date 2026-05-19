# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Mostrar opciones de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Selección de ingredientes
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),  # convertir a lista de strings
    max_selections=5
)

# Inicializar variable
time_to_insert = False

if ingredients_list:
    # Construir string de ingredientes
    ingredients_string = " ".join(ingredients_list)

    # Botón para insertar
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Ejecutar el INSERT en Snowflake
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered!', icon="✅")
         import requests  
        smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
        #st.text(smoothiefroot_response)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_contaner_width=True)
    

 

