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

# Smaller subtitle with markdown (using h3 for smaller size)
st.markdown("### Kies een vrij moment om te reserveren")

st.markdown('###')

# Adding a smaller banner image below the subtitle
st.image("oppem-logo.png", width=300)  # Banner is now half as small

# Create two columns for Saturday and Sunday
col1, col2 = st.columns(2)

with col1:
    st.subheader("Zaterdag")
    available_slots_saturday = get_slot_availability("Zaterdag")
    if available_slots_saturday:
        for slot in available_slots_saturday:
            timeslot = slot['Timeslot']
            current_reservations = slot['Aantal Reservaties']
            max_capacity = slot['Max Capaciteit']

            with st.expander(f"{timeslot} ({current_reservations}/{max_capacity} gereserveerd)"):
                with st.form(key=f'reservation_form_saturday_{timeslot}'):
                    name = st.text_input("Name", key=f'name_saturday_{timeslot}')
                    address = st.text_input("Address", key=f'address_saturday_{timeslot}')
                    email = st.text_input("Email", key=f'email_saturday_{timeslot}')
                    submit = st.form_submit_button(label=f'Book {timeslot}')

                    if submit:
                        if name and address and email:
                            make_reservation("Zaterdag", timeslot, name, address, email)
                        else:
                            st.error("Gelieve alle velden in te vullen")
    else:
        st.info("Alle timeslots voor zaterdag zijn volzet")

with col2:
    st.subheader("Zondag")
    available_slots_sunday = get_slot_availability("Zondag")
    if available_slots_sunday:
        for slot in available_slots_sunday:
            timeslot = slot['Timeslot']
            current_reservations = slot['Aantal Reservaties']
            max_capacity = slot['Max Capaciteit']

            with st.expander(f"{timeslot} ({current_reservations}/{max_capacity} gereserveerd)"):
                with st.form(key=f'reservation_form_sunday_{timeslot}'):
                    name = st.text_input("Name", key=f'name_sunday_{timeslot}')
                    address = st.text_input("Address", key=f'address_sunday_{timeslot}')
                    email = st.text_input("Email", key=f'email_sunday_{timeslot}')
                    submit = st.form_submit_button(label=f'Book {timeslot}')

                    if submit:
                        if name and address and email:
                            make_reservation("Zondag", timeslot, name, address, email)
                        else:
                            st.error("Gelieve alle velden in te vullen")
    else:
        st.info("Alle timeslots voor zondag zijn volzet")
