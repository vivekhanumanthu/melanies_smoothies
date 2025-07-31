# Import python packages
import streamlit as st
import requests
import pandas
from snowflake.snowpark.functions import col
# from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(f"custom smoothie order form :cup_with_straw: {st.__version__}")
st.write(
  """choose the fruit you want.
  """
)
name_on_order=st.text_input('enter name on smoothie')
st.write("Name on smoothie will be ",name_on_order)
cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))

# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list=st.multiselect(
    "choose upto 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)
if ingredients_list:
    ingredients_string=''

    for fruit_choosen in ingredients_list:
        ingredients_string+=fruit_choosen+' '
        search_on=pd_df.loc[pd_df['fruit_name'] == fruit_choosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_choosen,' is ', search_on, '.')
        st.subheader(fruit_choosen+' Nutrition Info')
        smoothiefroot_response = requests.get("https://fruityvice.com/api/fruit/"+search_on)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    time_to_insert=st.button("submit order")
    
    st.write(my_insert_stmt)
    # st.stop()
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


