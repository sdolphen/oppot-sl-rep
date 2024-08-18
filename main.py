import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

##------------------------- GOOGLE API SETUP ---------------------------##

# Set up the credentials using Streamlit secrets
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)

# Authorize the client
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open("Oppemevent").sheet1  # Replace with your Google Sheet name
reservation_sheet = client.open("Oppemevent").get_worksheet(1)  # Second sheet for reservations

# Function to check and update slot availability
def get_slot_availability(day):
    timeslots = sheet.get_all_records()
    available_slots = [slot for slot in timeslots if slot['Day'] == day and slot['Aantal Reservaties'] < slot['Max Capaciteit']]
    return available_slots

# Function to make a reservation
def make_reservation(day, timeslot, name, address, email):
    # Find the row with the matching day and timeslot
    cell = sheet.find(timeslot)
    current_reservations = int(sheet.cell(cell.row, 3).value)  # Assuming the third column is 'Aantal Reservaties'
    max_capacity = int(sheet.cell(cell.row, 4).value)  # Assuming the fourth column is 'Max Capaciteit'
    
    if current_reservations < max_capacity:
        sheet.update_cell(cell.row, 3, current_reservations + 1)
        # Add to the reservations sheet
        reservation_sheet.append_row([day, timeslot, name, address, email])
        st.success(f"Reservation for {timeslot} on {day} confirmed!")
    else:
        st.error("Sorry, this timeslot is fully booked.")

# App layout
st.title("SP Oppem Eetfestijn")
st.header("Kies een dag en een vrij moment om te reserveren")

# Select day
day = st.selectbox("Select Day", ["Saturday", "Sunday"])

available_slots = get_slot_availability(day)

if available_slots:
    for slot in available_slots:
        timeslot = slot['Timeslot']
        current_reservations = slot['Aantal Reservaties']
        max_capacity = slot['Max Capaciteit']

        with st.expander(f"{timeslot} ({current_reservations}/{max_capacity} reserved)"):
            with st.form(key=f'reservation_form_{day}_{timeslot}'):
                name = st.text_input("Name")
                address = st.text_input("Address")
                email = st.text_input("Email")
                submit = st.form_submit_button(label=f'Book {timeslot}')

                if submit:
                    if name and address and email:
                        make_reservation(day, timeslot, name, address, email)
                    else:
                        st.error("Please fill out all fields.")
else:
    st.info("All timeslots for the selected day are fully booked.")
