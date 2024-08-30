import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

##------------------------- GOOGLE API SETUP ---------------------------##

# Set page configuration
st.set_page_config(page_title="SP Oppem Eetfestijn", page_icon="oppem-logo.png")

# Set up the credentials using Streamlit secrets
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
)

# Authorize the client
client = gspread.authorize(credentials)

# Open the Google Sheets
sheet = client.open("Oppemevent").sheet1  # First sheet for timeslot management
reservation_sheet = client.open("Oppemevent").get_worksheet(1)  # Second sheet for reservations
email_sheet = client.open("Oppemevent").get_worksheet(2)  # Third sheet for storing emails

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
        st.success(f"Reservatie voor {timeslot} op {day} bevestigd!")
    else:
        st.error("Sorry, this timeslot is fully booked.")

# Function to save email for notifications
def save_email(email):
    email_sheet.append_row([email])
    st.success("Je e-mail adres is opgeslagen. We zullen je verwittigen zodra de link actief is.")

# Inject custom CSS for expander header text
st.markdown("""
    <style>
    /* Targeting the expander header text */
    .streamlit-expanderHeader div {
        color: #00FF00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Introductory text
st.title("Sporting Oppem - Eerste Spaghettiweekend")
st.write("""
Welkom bij Sporting Oppem en leuk dat u interesse hebt in ons Eerste Spaghettiweekend.
We zorgen ervoor dat je hier vanaf zaterdag 14 september zal kunnen reserveren (is niet verplicht) of kan bestellen om af te halen. 
We zullen volgende shiften doen:
""")

# Additional information and email capture
st.write("""
Zaterdag van 17u-18u30, van 18u30-20u en van 20u-21u30  
Zondag van 11u30-13u00 en van 13u-14u30  
Wil je graag verwittigd worden wanneer deze link actief zal zijn, laat dan hier je e-mail adres achter en we sturen jou een mailtje van zodra de reservaties en bestellingen kunnen geplaatst worden.
""")

# Email input field
email_input = st.text_input("E-mail adres", key="notification_email")
if st.button("Stuur mij een notificatie"):
    if email_input:
        save_email(email_input)
    else:
        st.error("Gelieve een geldig e-mail adres in te vullen.")

st.write("Tot snel!")

# Updated timeslots
updated_timeslots = {
    "Zaterdag": ["17u-18u30", "18u30-20u", "20u-21u30"],
    "Zondag": ["11u30-13u00", "13u-14u30"]
}

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

            if timeslot in updated_timeslots["Zaterdag"]:
                with st.expander(f"{timeslot} ({current_reservations}/{max_capacity} gereserveerd)"):
                    with st.form(key=f'reservation_form_saturday_{timeslot}'):
                        name = st.text_input("Naam", key=f'name_saturday_{timeslot}')
                        address = st.text_input("Adres", key=f'address_saturday_{timeslot}')
                        email = st.text_input("Email", key=f'email_saturday_{timeslot}')
                        submit = st.form_submit_button(label=f'Reserveer {timeslot}')

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

