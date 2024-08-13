import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", 
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
credentials = {
    "type": st.secrets["google"]["type"],
    "project_id": st.secrets["google"]["project_id"],
    "private_key_id": st.secrets["google"]["private_key_id"],
    "private_key": st.secrets["google"]["private_key"],
    "client_email": st.secrets["google"]["client_email"],
    "client_id": st.secrets["google"]["client_id"],
    "auth_uri": st.secrets["google"]["auth_uri"],
    "token_uri": st.secrets["google"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"]
}

# Authenticate and connect to Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)

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
    current_reservations = sheet.cell(cell.row, 3).value  # Assuming the third column is 'Current Reservations'
    if int(current_reservations) < 10:
        sheet.update_cell(cell.row, 3, int(current_reservations) + 1)
        # Add to the reservations sheet
        reservation_sheet.append_row([timeslot, name, address, email])
        st.success(f"Reservation for {timeslot} confirmed!")
    else:
        st.error("Sorry, this timeslot is fully booked.")

# App layout
st.title("SP Oppem Event Reservation")

st.header("Available Timeslots")
timeslots, available_slots = get_slot_availability()

for slot in timeslots:
    st.write(f"{slot['Timeslot']}: {slot['Current Reservations']}/{slot['Max Capacity']} reservations")
    if slot in available_slots:
        if st.button(f"Book {slot['Timeslot']}"):
            selected_slot = slot['Timeslot']
            with st.form(key='reservation_form'):
                name = st.text_input("Name")
                address = st.text_input("Address")
                email = st.text_input("Email")
                submit = st.form_submit_button(label='Submit Reservation')

                if submit and name and address and email:
                    make_reservation(selected_slot, name, address, email)

# Note: Add an error message if the form is not filled out properly.
