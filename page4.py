import streamlit as st
import pandas as pd
from st_files_connection import FilesConnection

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state='auto'
)

conn = st.connection('s3', type=FilesConnection)

# Initialize Session State for df0 if not present
if 'df0' not in st.session_state:
    st.session_state.df0 = conn.read("shakeys-image-labels/shakeys-labeled-data.csv", input_format="csv", ttl=0)

# List of Pizza Flavors
pizza_flavors = [
    "Classic Beef N' Onion Pizza Americana",
    "Classic Cheese Pizza Americana",
    "Classic Spinach Pizza Americana",
    "Glazed Bacon Pizza Americana",
    "Hawaiian Delight Pizza Americana",
    "Hi Protein Pizza Americana",
    "Angus Steakhouse Pizza",
    "Belly Buster",
    "Classic Beef N' Onion",
    "Classic Cheese",
    "Friday Special",
    "Garlic N Cheese",
    "Glazed Bacon",
    "Hawaiian Delight",
    "Hi Protein Supreme",
    "Manager's Choice",
    "Manager's Choice Pizza Americana",
    "Merry Pepperoni Holiday Pizza",
    "Pepperoni",
    "Pepperoni Crrrunch",
    "Pizza Bianca",
    "Pizza Bianca Pizza Americana",
    "Scallop Primo Pizza",
    "Shakey's Special",
    "Spinach & Glazed Bacon",
    "Spinach & Mushroom",
    "Spinach & Shrimp",
    "Texas Chicken BBQ",
    "Texas Chicken BBQ Pizza Americana",
    "Truffle Four Cheese",
    "Truffle Greens Pizza",
]

evaluation_options = ["Standard", "Non-Standard"]

store_servers = [
    "Quezon Avenue",
    "SM North Edsa",
    "UPS WOW Center",
    "Magallanes"
]
    
# Display the filtered DataFrame (df0)
st.markdown("### Classified Images")

start_date = None
end_date = None

# Get user input for start and end date
container = st.container()
with container:
    columns = st.columns((1, 1, 1, 1))
    with columns[0]:
        start_date = st.date_input("Start Date", start_date)
    with columns[1]:
        end_date = st.date_input("End Date", end_date)
    with columns[2]:
        selected_store_server = st.multiselect(
            "Select Store:",
            store_servers,
            placeholder='Please select a store',
        )
    with columns[3]:
        # Multiselect filter for 'Pizza Classification'
        selected_pizza_classifications = st.multiselect(
            "Filter by Pizza Flavor:",
            pizza_flavors,
        )

# Convert datetime64[ns] to date for comparison
st.session_state.df0["Date"] = pd.to_datetime(st.session_state.df0["Date"]).dt.date

# Filter the DataFrame based on user input if dates are provided
if start_date is not None and end_date is not None:
    # Filter the DataFrame based on user input
    filtered_df0 = st.session_state.df0[
        (st.session_state.df0["Date"] >= start_date) & (st.session_state.df0["Date"] <= end_date)
    ].copy()
else:
    # If no dates are provided, show the entire DataFrame
    filtered_df0 = st.session_state.df0.copy()

# Filter the DataFrame based on other user selections
if selected_pizza_classifications:
    filtered_df0 = filtered_df0[filtered_df0["Pizza Classification"].isin(selected_pizza_classifications)]

if selected_store_server:
    filtered_df0 = filtered_df0[filtered_df0["Branch"].isin(selected_store_server)]

# Reset index
filtered_df0.reset_index(drop=True, inplace=True)

# Configure the SelectboxColumn for "Pizza Classification"
classification_column_config = st.column_config.SelectboxColumn(
    "Pizza Classification",
    options=pizza_flavors,
    width="medium",
    required=True, 
)

# Configure the SelectboxColumn for "Pizza Evaluation"
evaluation_column_config = st.column_config.SelectboxColumn(
    "Pizza Evaluation",
    options=evaluation_options,
    width="medium",
    required=True,  
)

# Configure the SelectboxColumn for "Pizza Evaluation"
status_config = st.column_config.SelectboxColumn(
    "Status",
    options=["Accepted", "Rejected"],
    required=True, 
)

# Save Button
columns2 = st.columns((1, 1, 1, 1, 1))
with columns2[0]:
    save_button = st.button("Save Changes", help="You can modify the 'Pizza Classification,' 'Pizza Evaluation,' and 'Status' of the image, just double-click the corresponding cell and choose a new value from the selection. After selecting a new value, click the 'Save Changes' button to apply the changes. Keep in mind that selecting new values without clicking the button will not capture the changes")

with columns2[2]:
    num_rows = len(filtered_df0)
    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>Images classified: {num_rows}</p>", unsafe_allow_html=True)        

# Display the DataFrame with st.data_editor
st.data_editor(
    filtered_df0,
    key="edit_key",
    disabled=("Branch", "Event ID", "Date", "Time"),
    column_config={
        "Pizza Image": st.column_config.ImageColumn(
            label="Pizza Image", help="Pizza image preview"
        ),
        "Zoomed": st.column_config.ImageColumn(
            label="Zoomed", help="Zoomed image preview"
        ),
        "Pizza Classification": classification_column_config,
        "Pizza Evaluation": evaluation_column_config,
        "Status": status_config,
    },
    use_container_width=True
)

# Parse the JSON data from st.data_editor
edit_data = st.session_state.edit_key

# Update the DataFrame based on the edited rows when Save button is clicked
if save_button and "edited_rows" in edit_data:
    for index_str, changes in edit_data["edited_rows"].items():
        index = int(index_str)
        for column, new_value in changes.items():
            st.session_state.df0.at[index, column] = new_value
    
    #st.session_state.df0.to_csv('csv/shakeys-labeled-data.csv', index=False)
    with conn.open('shakeys-image-labels/shakeys-labeled-data.csv', 'wb') as f:
        st.session_state.df0.to_csv(f, index=False)

    # Trigger a rerun to refresh the page
    st.rerun()


