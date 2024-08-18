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
def get_slot_availability():
    timeslots = sheet.get_all_records()
    available_slots = [slot for slot in timeslots if slot['Current Reservations'] < slot['Max Capacity']]
    return timeslots, available_slots

# Function to make a reservation
def make_reservation(timeslot, name, address, email):
    # Update the main sheet's reservation count
    cell = sheet.find(timeslot)
    current_reservations = int(sheet.cell(cell.row, 3).value)  # Assuming the third column is 'Current Reservations'
    if current_reservations < 10:
        sheet.update_cell(cell.row, 3, current_reservations + 1)
        # Add to the reservations sheet
        reservation_sheet.append_row([timeslot, name, address, email])
        st.success(f"Reservation for {timeslot} confirmed!")
    else:
        st.error("Sorry, this timeslot is fully booked.")

# App layout
st.title("SP Oppem Event Reservation")

st.header("Available Timeslots")
timeslots, available_slots = get_slot_availability()

# Display available timeslots and reservation forms
for slot in timeslots:
    timeslot = slot['Timeslot']
    current_reservations = slot['Current Reservations']
    max_capacity = slot['Max Capacity']

    st.write(f"{timeslot}: {current_reservations}/{max_capacity} reservations")
    
    if current_reservations < max_capacity:
        with st.form(key=f'reservation_form_{timeslot}'):
            name = st.text_input("Name")
            address = st.text_input("Address")
            email = st.text_input("Email")
            submit = st.form_submit_button(label=f'Book {timeslot}')

            if submit:
                if name and address and email:
                    make_reservation(timeslot, name, address, email)
                else:
                    st.error("Please fill out all fields.")
