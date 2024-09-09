import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import WorksheetNotFound

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

# Open the Google Sheet
sheet = client.open("Oppemevent").sheet1  # Replace with your Google Sheet name
reservation_sheet = client.open("Oppemevent").get_worksheet(1)  # Second sheet for reservations

# Check if the third worksheet exists, if not, create it
try:
    email_list_sheet = client.open("Oppemevent").get_worksheet(2)  # Third sheet for collecting email addresses
except WorksheetNotFound:
    # Create the worksheet if it doesn't exist
    email_list_sheet = client.open("Oppemevent").add_worksheet(title="Email List", rows="1000", cols="2")

# Function to check and update slot availability
def get_slot_availability(day):
    timeslots = sheet.get_all_records()
    available_slots = [slot for slot in timeslots if slot['Day'] == day and slot['Aantal Personen'] < 60]  # Max 60 people per slot
    return available_slots

# Function to make a reservation
def make_reservation(day, timeslot, first_name, last_name, num_persons, phone_number, special_request):
    # Find the row with the matching day and timeslot
    cell = sheet.find(timeslot)
    current_persons = int(sheet.cell(cell.row, 3).value)  # Assuming the third column is 'Aantal Personen'
    max_capacity = 60  # Max capacity for each slot is 60 people
    
    if current_persons + num_persons <= max_capacity:
        sheet.update_cell(cell.row, 3, current_persons + num_persons)
        # Add to the reservations sheet
        reservation_sheet.append_row([day, timeslot, first_name, last_name, num_persons, phone_number, special_request])
        st.success(f"Reservatie voor {timeslot} op {day} bevestigd! ({num_persons} personen)")
    else:
        st.error(f"Sorry, this timeslot is fully booked. Nog {max_capacity - current_persons} plaatsen beschikbaar.")

# Function to collect email addresses
def collect_email(email):
    email_list_sheet.append_row([email])
    st.success("Je email is opgeslagen! We laten je weten wanneer de link actief is.")

# Display the logo at the top and make it smaller using st.image
st.image("oppem-logo.png", width=75)

# Introductory text
st.title("Spaghettiweekend SP Oppem")
st.write("""
Welkom bij Sporting Oppem en leuk dat u interesse hebt in ons Eerste Spaghettiweekend.  

Indien u graag vooraf reserveert (geen wachttijd) of indien u graag wil afhalen, dan kan dit via ons onderstaande invulformulier.

Op het menu staat er natuurlijk spaghetti (zowel zonder als met vlees), met als alternatief een croque monsieur. Je kan achteraf ook nog een dessertje kiezen.

Voor de reservaties werken we met shiften van telkens anderhalf uur. Je kan kiezen uit volgende shiften:
""")

# Highlighted text with custom background color
st.markdown(
    """
    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 1.1em;">
        <strong>Zaterdag van 17u-18u30, van 18u30-20u en van 20u-21u30</strong><br>
        <strong>Zondag van 11u30-13u00 en van 13u-14u30</strong>
    </div>
    """, 
    unsafe_allow_html=True
)
st.write("")
# New text and email input field
st.write("""
Indien u liever wenst af te halen, dan kan u hieronder een bestelling plaatsen.

Is er iets niet duidelijk of hebt u andere vragen, stuur ons gerust een mailtje.

e-mail adres: secretariaat.sportingoppem@outlook.be

Dank nogmaals en tot dan!""")

email = st.text_input("E-mail adres", key="notification_email")
if st.button("Indienen"):
    if email:
        collect_email(email)
    else:
        st.error("Gelieve een geldig e-mail adres in te vullen")

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
            current_persons = slot['Aantal Personen']
            max_capacity = 60

            if timeslot in updated_timeslots["Zaterdag"]:
                with st.expander(f"{timeslot} ({current_persons}/{max_capacity} personen gereserveerd)"):
                    with st.form(key=f'reservation_form_saturday_{timeslot}'):
                        first_name = st.text_input("Voornaam", key=f'first_name_saturday_{timeslot}')
                        last_name = st.text_input("Naam", key=f'last_name_saturday_{timeslot}')
                        num_persons = st.number_input("Aantal personen", min_value=1, step=1, key=f'num_persons_saturday_{timeslot}')
                        phone_number = st.text_input("Tel. nummer", key=f'phone_saturday_{timeslot}')
                        special_request = st.text_area("Speciale wens", key=f'special_wish_saturday_{timeslot}')
                        submit = st.form_submit_button(label=f'Reserveer {timeslot}')

                        if submit:
                            if first_name and last_name and num_persons and phone_number:
                                make_reservation("Zaterdag", timeslot, first_name, last_name, num_persons, phone_number, special_request)
                            else:
                                st.error("Gelieve alle verplichte velden in te vullen")
    else:
        st.info("Alle timeslots voor zaterdag zijn volzet")

with col2:
    st.subheader("Zondag")
    available_slots_sunday = get_slot_availability("Zondag")
    if available_slots_sunday:
        for slot in available_slots_sunday:
            timeslot = slot['Timeslot']
            current_persons = slot['Aantal Personen']
            max_capacity = 60

            if timeslot in updated_timeslots["Zondag"]:
                with st.expander(f"{timeslot} ({current_persons}/{max_capacity} personen gereserveerd)"):
                    with st.form(key=f'reservation_form_sunday_{timeslot}'):
                        first_name = st.text_input("Voornaam", key=f'first_name_sunday_{timeslot}')
                        last_name = st.text_input("Naam", key=f'last_name_sunday_{timeslot}')
                        num_persons = st.number_input("Aantal personen", min_value=1, step=1, key=f'num_persons_sunday_{timeslot}')
                        phone_number = st.text_input("Tel. nummer", key=f'phone_sunday_{timeslot}')
                        special_request = st.text_area("Speciale wens", key=f'special_wish_sunday_{timeslot}')
                        submit = st.form_submit_button(label=f'Reserveer {timeslot}')

                        if submit:
                            if first_name and last_name and num_persons and phone_number:
                                make_reservation("Zondag", timeslot, first_name, last_name, num_persons, phone_number, special_request)
                            else:
                                st.error("Gelieve alle verplichte velden in te vullen")
    else:
        st.info("Alle timeslots voor zondag zijn volzet")
