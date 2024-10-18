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

Helaas zijn de reservaties en bestellingen nu afgesloten, maar u kan zeker langskomen zonder reservatie. Tot dan!
""")
