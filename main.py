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

# Function to check and update slot availability with proper key names
def get_slot_availability(day):
    timeslots = sheet.get_all_records()
    
    # Correct column name to 'Aantal Reservaties'
    available_slots = [
        slot for slot in timeslots 
        if slot['Day'] == day and int(slot['Aantal Personen']) < 60  # Max 60 people per slot
    ]
    
    return available_slots


# Function to make a reservation
def make_reservation(day, timeslot, first_name, last_name, email_address, num_persons, phone_number, special_request):
    try:
        # Find the row with the matching day and timeslot
        cell = sheet.find(timeslot)
        
        # Fetch the current number of people from the 'Aantal Reservaties' column
        current_reservations_str = sheet.cell(cell.row, sheet.find("Aantal Personen").col).value
        current_reservations = int(current_reservations_str) if current_reservations_str.isdigit() else 0
        
        # Fetch the max capacity from the 'Max Capaciteit' column
        max_capacity_str = sheet.cell(cell.row, sheet.find("Max Capaciteit").col).value
        max_capacity = int(max_capacity_str) if max_capacity_str.isdigit() else 60  # Default to 60 if missing
        
        # Check if there is enough room for the number of people in this reservation
        if current_reservations + num_persons <= max_capacity:
            # Update the number of people in the 'Aantal Reservaties' column
            sheet.update_cell(cell.row, sheet.find("Aantal Personen").col, current_reservations + num_persons)
            
            # Add the reservation details to the reservation sheet (including the email)
            reservation_sheet.append_row([day, timeslot, first_name, last_name, email_address, num_persons, phone_number, special_request])
            
            # Confirm the reservation
            st.success(f"Reservatie voor {timeslot} op {day} bevestigd! ({num_persons} personen)")
        else:
            # If the slot is full, show an error
            available_spots = max_capacity - current_reservations
            st.error(f"Sorry, this timeslot is fully booked. Nog {available_spots} plaatsen beschikbaar.")
    
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het maken van de reservatie: {e}")

def make_reservation_afhaal(day, timeslot, first_name, last_name, email_address, phone_number, num_bolognaise, num_veggie, num_saus_bolognaise, num_saus_veggie, special_request):
    try:
        # Append the order details, including the specific information, to the third worksheet (pickup orders)
        email_list_sheet.append_row([  # Assuming the third sheet is used for pickup orders
            day, timeslot, first_name, last_name, email_address, phone_number,
            num_bolognaise, num_veggie, num_saus_bolognaise, num_saus_veggie, special_request
        ])
        
        # Confirm the reservation
        st.success(f"Afhaalreservatie voor {timeslot} op {day} bevestigd! ({num_bolognaise} bolognaise, {num_veggie} veggie, {num_saus_bolognaise} saus bolognaise, {num_saus_veggie} saus veggie)")
    
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij het maken van de afhaalreservatie: {e}")




# Display the logo at the top and make it smaller using st.image
st.image("oppem-logo.png", width=75)

# Introductory text
st.title("Spaghettiweekend SP Oppem")
st.write("""
Welkom bij Sporting Oppem en leuk dat u interesse hebt in ons Eerste Spaghettiweekend.  

Indien u graag vooraf reserveert (geen wachttijd) of indien u graag wil afhalen, dan kan dit via ons onderstaande invulformulier.

Op het menu staat er natuurlijk spaghetti (zowel zonder als met vlees), met als alternatief een croque monsieur. U kan achteraf ook nog een dessertje kiezen.

Voor de reservaties werken we met shiften van telkens anderhalf uur. U kan kiezen uit volgende shiften:
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

st.subheader("Reserveren")

# Updated timeslots
updated_timeslots = {
    "Zaterdag": ["17u-18u30", "18u30-20u", "20u-21u30"],
    "Zondag": ["11u30-13u00", "13u-14u30"]
}

# Create two columns for Saturday and Sunday
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Zaterdag")
    available_slots_saturday = get_slot_availability("Zaterdag")
    if available_slots_saturday:
        for slot in available_slots_saturday:
            timeslot = slot['Timeslot']
            current_persons = slot['Aantal Personen']
            max_capacity = 60

            if timeslot in updated_timeslots["Zaterdag"]:
                with st.expander(f"{timeslot} ({current_persons}/{max_capacity} personen gereserveerd)"):
                    with st.form(key=f'reservation_form_saturday_{timeslot}'):
                        # Add email input field in the reservation forms for Saturday and Sunday
                        first_name = st.text_input("Voornaam", key=f'first_name_saturday_{timeslot}')
                        last_name = st.text_input("Naam", key=f'last_name_saturday_{timeslot}')
                        email_address = st.text_input("Email", key=f'email_saturday_{timeslot}')  # New email field
                        num_persons = st.number_input("Aantal personen", min_value=1, step=1, key=f'num_persons_saturday_{timeslot}')
                        phone_number = st.text_input("Tel. nummer", key=f'phone_saturday_{timeslot}')
                        special_request = st.text_area("Speciale wens", key=f'special_wish_saturday_{timeslot}')
                        submit = st.form_submit_button(label=f'Reserveer {timeslot}')

                        if submit:
                            if first_name and last_name and email_address and num_persons and phone_number:
                                make_reservation("Zaterdag", timeslot, first_name, last_name, email_address, num_persons, phone_number, special_request)
                            else:
                                st.error("Gelieve alle velden in te vullen")

    else:
        st.info("Alle timeslots voor zaterdag zijn volzet")

with col2:
    st.markdown("##### Zondag")
    available_slots_sunday = get_slot_availability("Zondag")
    if available_slots_sunday:
        for slot in available_slots_sunday:
            timeslot = slot['Timeslot']
            current_persons = slot['Aantal Personen']
            max_capacity = 60

            if timeslot in updated_timeslots["Zondag"]:
                with st.expander(f"{timeslot} ({current_persons}/{max_capacity} personen gereserveerd)"):
                    with st.form(key=f'reservation_form_sunday_{timeslot}'):
                        # Add email input field in the reservation form for Sunday
                        first_name = st.text_input("Voornaam", key=f'first_name_sunday_{timeslot}')
                        last_name = st.text_input("Naam", key=f'last_name_sunday_{timeslot}')
                        email_address = st.text_input("Email", key=f'email_sunday_{timeslot}')  # New email field
                        num_persons = st.number_input("Aantal personen", min_value=1, step=1, key=f'num_persons_sunday_{timeslot}')
                        phone_number = st.text_input("Tel. nummer", key=f'phone_sunday_{timeslot}')
                        special_request = st.text_area("Speciale wens", key=f'special_wish_sunday_{timeslot}')
                        submit = st.form_submit_button(label=f'Reserveer {timeslot}')

                        if submit:
                            if first_name and last_name and email_address and num_persons and phone_number:
                                make_reservation("Zondag", timeslot, first_name, last_name, email_address, num_persons, phone_number, special_request)
                            else:
                                st.error("Gelieve alle velden in te vullen")

    else:
        st.info("Alle timeslots voor zondag zijn volzet")

# Add this below your Sunday reservation code to include the "Afhalen" slots
st.markdown("""""")
st.markdown("""""")

# Timeslots for pickup
st.subheader("Afhalen")
st.write("""
U kan een bestelling plaatsen om af te halen tijdens ons eetfestijn. Hierbij kan u een aantal porties kiezen en/of u kan ook enkel saus bestellen.
De porties zijn verpakt per persoon en zijn inclusief pasta / saus en een potje kaas. U kan kiezen uit een saus met vlees of zonder vlees. 
Ook is het mogelijk om enkel saus te bestellen, in bolognaise of veggie variant, per halve liter.
""")

# Timeslots for pickup
pickup_timeslots = {
    "Afhalen": ["Zaterdag 16u00-21u00", "Zondag 11u00-15u00"]
}

# Create a section for pickup reservations
available_slots_pickup = get_slot_availability("Afhalen")
if available_slots_pickup:
    for slot in available_slots_pickup:
        timeslot = slot['Timeslot']
        current_persons = slot['Aantal Personen']
        max_capacity = 60

        if timeslot in pickup_timeslots["Afhalen"]:
            with st.expander(f"{timeslot} ({current_persons}/{max_capacity} personen gereserveerd)"):
                with st.form(key=f'reservation_form_pickup_{timeslot}'):
                    # Input fields for pickup reservations
                    first_name = st.text_input("Voornaam", key=f'first_name_pickup_{timeslot}')
                    last_name = st.text_input("Achternaam", key=f'last_name_pickup_{timeslot}')  # Add last name field
                    num_bolognaise = st.number_input("Aantal porties bolognaise (€ 12 per portie)", min_value=0, step=1, key=f'num_bolognaise_pickup_{timeslot}')
                    num_veggie = st.number_input("Aantal porties veggie (€ 12 per portie)", min_value=0, step=1, key=f'num_veggie_pickup_{timeslot}')
                    num_saus_bolognaise = st.number_input("Enkel bolognaise saus per halve liter (€ 12 per halve liter)", min_value=0, step=1, key=f'num_saus_bolognaise_pickup_{timeslot}')
                    num_saus_veggie = st.number_input("Enkel veggie saus per halve liter (€ 12 per halve liter)", min_value=0, step=1, key=f'num_saus_veggie_pickup_{timeslot}')
                    phone_number = st.text_input("Tel. nummer", key=f'phone_pickup_{timeslot}')
                    email_address = st.text_input("Email", key=f'email_pickup_{timeslot}')
                    
                    # Submit button
                    submit = st.form_submit_button(label=f'Reserveer {timeslot}')
                    
                    # Validation to ensure mandatory fields are filled
                    if submit:
                        if first_name and last_name and phone_number and email_address:
                            total_items = num_bolognaise + num_veggie + num_saus_bolognaise + num_saus_veggie
                            if total_items > 0:
                                # Pass the order details to make_reservation
                                make_reservation_afhaal(
                                    "Afhalen", timeslot, first_name, last_name, email_address, phone_number,
                                    num_bolognaise, num_veggie, num_saus_bolognaise, num_saus_veggie, ""
                                )
                            else:
                                st.error("Gelieve minstens één portie te selecteren.")
                        else:
                            st.error("Gelieve alle verplichte velden in te vullen (Voornaam, Achternaam, Tel. nummer, e-mail adres).")

else:
    st.info("Alle timeslots voor afhalen zijn volzet")

