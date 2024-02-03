import streamlit as st
import pandas as pd
from st_pages import Page, show_pages
from st_files_connection import FilesConnection
#s3fs

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state='auto'
)

#st.markdown('<style>div.block-container{padding-top:1.5rem;}</style>', unsafe_allow_html=True)

show_pages(
    [
        Page("app.py", "Pending Classification"),
        Page("page2.py", "Standard"),
        Page("page3.py", "Non-Standard"),
        Page("page4.py", "Classified Images"),
        Page("page5.py", "Live"),
    ]
)

# csv_file_path1 = 'csv/conso_filtered_event_data.csv'
# csv_file_path2 = 'csv/shakeys-labeled-data.csv'
conn = st.connection('s3', type=FilesConnection)
csv_file_path1 = "shakeys-image-labels/conso_filtered_event_data.csv"
csv_file_path2 = "shakeys-image-labels/shakeys-labeled-data.csv"

# Initialize Session State for df if not present
if 'df' not in st.session_state:
    # st.session_state.df = pd.read_csv(csv_file_path1)
    st.session_state.df = conn.read(csv_file_path1, input_format="csv", ttl=0)

# Initialize Session State for df0 if not present
if 'df0' not in st.session_state:
    st.session_state.df0 = conn.read(csv_file_path2, input_format="csv", ttl=0)

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

st.session_state.pizza_flavors = pizza_flavors
st.session_state.evaluation_options = evaluation_options

store_servers = [
    "Quezon Avenue",
    "SM North Edsa",
    "UPS WOW Center",
    "Magallanes"
]

# Add 'All' option to the list of store servers
store_servers_with_all = ['All Stores'] + store_servers

selected_store_server = st.multiselect(
    "Select Store:",
    store_servers_with_all,
    placeholder='Please select a store',
    help="Choose a store to start labeling the images. You have the option to select multiple stores for labeling, or you can choose the 'All Stores' option to filter the table with all available stores",
)

container = st.container(border=1)

# Initialize start_date and end_date to None by default
start_date = None
end_date = None

# Get user input for start and end date
container2 = st.container(border=1)
with container2:
    # Display the filtered DataFrame (df)
    st.markdown("<p style='font-size: 30px; font-weight: bold;'>Pending Classification</p>",
                unsafe_allow_html=True)
    
    columns2 = st.columns((1, 1))
    with columns2[0]:
        columns3 = st.columns((1, 1))
        with columns3[0]:
            start_date = st.date_input("Start Date", start_date)
        with columns3[1]:
            end_date = st.date_input("End Date", end_date,
                                     help="If you want to filter the table by date, simply select a date from both the start date and end date filters")
    with columns2[1]:
        columns4 = st.columns((1, 1, 1))
        with columns4[1]:
            container4 = st.container()

# Filter the DataFrame based on user input if dates are provided
if start_date is not None and end_date is not None:
    # Convert datetime64[ns] to date for comparison
    st.session_state.df["Date"] = pd.to_datetime(st.session_state.df["Date"]).dt.date

    # Filter the DataFrame based on user input
    filtered_df = st.session_state.df[
        (st.session_state.df["Date"] >= start_date) & (st.session_state.df["Date"] <= end_date)
    ].copy()

    # Filter the DataFrame based on the selected store servers (Branch)
    if selected_store_server:
        filtered_df = filtered_df[filtered_df["Branch"].isin(selected_store_server)]

    # Reset index
    filtered_df.reset_index(drop=True, inplace=True)
else:
    # If no dates are provided, show the entire DataFrame
    filtered_df = st.session_state.df.copy()

# Filter the DataFrame based on the selected store servers (Branch)
if 'All Stores' in selected_store_server:
    # Include all stores if 'All' is selected
    filtered_df = filtered_df.copy()
elif selected_store_server:
    filtered_df = filtered_df[filtered_df["Branch"].isin(selected_store_server)]
else:
    filtered_df = pd.DataFrame()

# Reset index
filtered_df.reset_index(drop=True, inplace=True)

with container:
    columns = st.columns((1, 1))
    with columns[0]:   
        # Form to encapsulate widgets
        with st.form(key='my_form'):

            st.markdown("<p style='font-size: 30px; font-weight: bold;'>To Classify</p>", unsafe_allow_html=True)
            # Dropdown for selecting pizza flavor
            selected_pizza_flavor = st.selectbox(
                "Select Pizza Flavor:",
                pizza_flavors,
                index=None,
                placeholder="Select pizza flavor...",
                help="Use the dropdown menu to select the correct pizza flavor",
            )

            # Dropdown for selecting label type
            label_type = st.selectbox(
                "Select Evaluation:",
                evaluation_options,
                index=None,
                placeholder="Select evaluation...",
                help="Use the dropdown menu to select whether the pizza is Standard or Non-Standard",
            )

            container1 = st.container()
            with container1:
                columns1 = st.columns((1, 1))

                with columns1[0]:
                    save_label = "Accept Image"
                    is_save = st.form_submit_button(label=save_label, help="After selecting the pizza flavor and the evaluation, click the 'Accept Image' button to save the selected label")

                with columns1[1]:
                    discard_label = "Reject Image"
                    is_discard = st.form_submit_button(label=discard_label, help="If the image doesn't clearly show a pizza, for example, if an object is blocking the pizza, click the 'Reject Image' button to reject the image. Note that the image will still be saved in the 'Classified Images' tab but without any labels")

            # Update DataFrame based on button clicks
            if is_save:
                if not filtered_df.empty:
                    # Check if both selected_pizza_flavor and label_type have valid values
                    if selected_pizza_flavor is None and label_type is None:
                        st.warning('Please select the labels.')
                    else:
                        # Create a new DataFrame (df0) with the first row
                        df0 = pd.DataFrame(filtered_df.iloc[0]).T
                        df0['Pizza Classification'] = selected_pizza_flavor
                        df0['Pizza Evaluation'] = label_type
                        df0['Status'] = 'Accepted'

                        # Drop the first row from the filtered DataFrame
                        filtered_df = filtered_df.drop(filtered_df.index[0])

                        # Concatenate the new DataFrame (df0) to the session state DataFrame (df0)
                        st.session_state.df0 = pd.concat([df0, st.session_state.df0], ignore_index=True)

                        # Sort df0 by date in ascending order
                        st.session_state.df0['Date'] = pd.to_datetime(st.session_state.df0['Date'])
                        st.session_state.df0 = st.session_state.df0.sort_values(by='Date', ascending=False).reset_index(drop=True)
                        with conn.open(csv_file_path2, 'wb') as f:
                            st.session_state.df0.to_csv(f, index=False)
                        #st.session_state.df0.to_csv(csv_file_path2, index=False)

                        # Identify the rows in st.session_state.df that have the same "Event ID" as df0
                        rows_to_drop = st.session_state.df[st.session_state.df["Event ID"].isin(st.session_state.df0["Event ID"])].index

                        # Drop the identified rows from st.session_state.df
                        st.session_state.df = st.session_state.df.drop(index=rows_to_drop).reset_index(drop=True)

                        # Save the updated DataFrame back to the CSV file
                        with conn.open(csv_file_path1, 'wb') as f:
                            st.session_state.df.to_csv(f, index=False)
                        #st.session_state.df.to_csv(csv_file_path1, index=False)

                        st.success('Image Accepted.')
                else:
                    st.warning('There is no image to label.')

            elif is_discard:
                if not filtered_df.empty:

                    # Create a new DataFrame (df0) with the first row, without labels
                    df0 = pd.DataFrame(filtered_df.iloc[0]).T
                    df0['Pizza Classification'] = None
                    df0['Pizza Evaluation'] = None
                    df0['Status'] = 'Rejected'

                    # Drop the first row from the filtered DataFrame
                    filtered_df = filtered_df.drop(filtered_df.index[0])

                    # Concatenate the new DataFrame (df0) to the session state DataFrame (df0)
                    st.session_state.df0 = pd.concat([df0, st.session_state.df0], ignore_index=True)

                    # Sort df0 by date in ascending order
                    st.session_state.df0['Date'] = pd.to_datetime(st.session_state.df0['Date'])
                    st.session_state.df0 = st.session_state.df0.sort_values(by='Date', ascending=False).reset_index(drop=True)
                    with conn.open(csv_file_path2, 'wb') as f:
                        st.session_state.df0.to_csv(f, index=False)
                    #st.session_state.df0.to_csv(csv_file_path2, index=False)

                    # Identify the rows in st.session_state.df that have the same "Event ID" as df0
                    rows_to_drop = st.session_state.df[st.session_state.df["Event ID"].isin(st.session_state.df0["Event ID"])].index

                    # Drop the identified rows from st.session_state.df
                    st.session_state.df = st.session_state.df.drop(index=rows_to_drop).reset_index(drop=True)

                    # Save the updated DataFrame back to the CSV file
                    with conn.open(csv_file_path1, 'wb') as f:
                        st.session_state.df.to_csv(f, index=False)
                    #st.session_state.df.to_csv(csv_file_path1, index=False)

                    st.error('Image Rejected')

                else:
                    st.warning('There is no image to label.')

    with columns[1]:
        container3 = st.container(border=1)
        with container3:
            # Display the dynamic image from the "Pizza Image" column of the current DataFrame (df)
            if not filtered_df.empty:
                tab1, tab2 = st.tabs(["Pizza Image", "Zoomed Image"])
                with tab1:
                    st.image(filtered_df.iloc[0]['Pizza Image'])
                with tab2:
                    st.image(filtered_df.iloc[0]['Zoomed'])

                # Add next and back buttons to switch between 'Pizza Image' and 'Zoomed'
                button_col = st.columns((1, 1, 1))

                with button_col[0]:
                    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>Branch: {filtered_df.iloc[0]['Branch']}</p>", unsafe_allow_html=True)
                with button_col[1]:
                    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>Event ID: {filtered_df.iloc[0]['Event ID']}</p>", unsafe_allow_html=True)     
                with button_col[2]:
                    st.markdown(f"<p style='font-size: 14px; font-weight: bold;'>Date: {filtered_df.iloc[0]['Date']} | {filtered_df.iloc[0]['Time']}</p>", unsafe_allow_html=True)         
            else:
                # Display a default image when DataFrame is empty
                st.image('static/shakeys_logo.png', use_column_width="auto")  

with container4:
    container4.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    num_rows = len(filtered_df)
    st.markdown(f"<p style='font-size: 20px; font-weight: bold;'>Images to classify: {num_rows}</p>", unsafe_allow_html=True)        

with container2:
    st.data_editor(
        filtered_df,
        disabled=("Branch", "Event ID", "Date", "Time", "Pizza Classification", "Pizza Evaluation"),
        column_config={
            "Pizza Image": st.column_config.ImageColumn(
                label="Pizza Image", help="Pizza image preview"
            ),
            "Zoomed": st.column_config.ImageColumn(
                label="Zoomed", help="Zoomed image preview"
            ),
        },
        use_container_width=True  # Use the container width for st.data_editor
    )