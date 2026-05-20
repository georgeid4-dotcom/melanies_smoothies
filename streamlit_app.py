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

# Crear el Snowpark DataFrame con FRUIT_NAME y SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convertir el Snowpark DataFrame a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Mostrar el DataFrame para verificar los datos
st.dataframe(pd_df, use_container_width=True)

# Selección de ingredientes usando FRUIT_NAME
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Obtener el valor SEARCH_ON correspondiente a la fruta elegida
        search_values = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']

        if not search_values.empty and pd.notna(search_values.iloc[0]):
            search_on = search_values.iloc[0]
            st.write('The search value for', fruit_chosen, 'is', search_on, '.')

            # Mostrar subtítulo con el nombre de la fruta
            st.subheader(fruit_chosen + ' Nutrition Information')

            # Llamada a la API usando SEARCH_ON
            try:
                smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on.lower())
                smoothiefroot_response.raise_for_status()
                sf_df = pd.DataFrame([smoothiefroot_response.json()])
                st.dataframe(sf_df, use_container_width=True)
            except requests.exceptions.HTTPError as e:
                if smoothiefroot_response.status_code == 404:
                    st.warning(f"No nutrition data found for {fruit_chosen}, but it will still be added to your order.")
                else:
                    st.error(f"Could not retrieve data for {fruit_chosen}: {e}")
        else:
            st.error(f"No SEARCH_ON value found for {fruit_chosen}. Please check your table.")

    # Botón para insertar el pedido
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie with {ingredients_string.strip()} is ordered!", icon="✅")
