# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Title and description
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled")

# Establish Snowflake connection and session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch pending orders
try:
    my_dataframe = session.table("smoothies.public.orders") \
                          .filter(col("ORDER_FILLED") == 0) \
                          .collect()  # Collect results as a list of Row objects

    if not my_dataframe:
        st.success('There are no pending orders right now', icon="👍")
    else:
        # Convert to a list of dictionaries for display and editing
        editable_data = [row.as_dict() for row in my_dataframe]

        # Display editable table in Streamlit
        editable_df = st.data_editor(editable_data)

        # Update button
        if st.button('Submit'):
            try:
                # Convert edited data back to Snowpark DataFrame
                edited_dataset = session.create_dataframe(editable_df)

                # Merge updates
                session.table("smoothies.public.orders") \
                       .merge(
                           edited_dataset,
                           on=(col("ORDER_UID") == edited_dataset.col("ORDER_UID")),
                           when_matched=[when_matched().update({'ORDER_FILLED': edited_dataset.col("ORDER_FILLED")})]
                       )
                st.success("Order(s) Updated!", icon="👍")
            except Exception as e:
                st.error(f"Something went wrong during update: {e}")
except Exception as e:
    st.error(f"Error fetching data: {e}")
