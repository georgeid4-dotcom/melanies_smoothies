import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be:", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Traer opciones de frutas
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df, use_container_width=True)

# Selección de ingredientes
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Formato limpio con comas
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_values = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']

        if not search_values.empty and pd.notna(search_values.iloc[0]):
            search_on = search_values.iloc[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")

            try:
                # Llamada directa al dominio real
                smoothiefroot_response = requests.get(
                    f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}",
                    timeout=5
                )
                smoothiefroot_response.raise_for_status()
                sf_df = pd.DataFrame([smoothiefroot_response.json()])
                st.dataframe(sf_df, use_container_width=True)
            except requests.exceptions.HTTPError as e:
                if smoothiefroot_response.status_code == 404:
                    st.warning(f"No nutrition data found for {fruit_chosen}, but it will still be added to your order.")
                else:
                    st.error(f"Could not retrieve data for {fruit_chosen}: {e}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error for {fruit_chosen}: {e}")
        else:
            st.error(f"No SEARCH_ON value found for {fruit_chosen}. Please check your table.")

    # Insertar pedido en Snowflake
    if st.button('Submit Order'):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie with {ingredients_string} is ordered!", icon="✅")
