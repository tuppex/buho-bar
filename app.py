import streamlit as st
from streamlit_option_menu import option_menu
from google_sheets import GoogleSheets
import uuid
from google_calendar import GoogleCalendar
import numpy as np
import datetime as dt

##VARIABLES
page_title = "Buho bar"
page_icon = "assets/icono.bmp"
layout = "centered"

horas = ["21:00"]
pistas = ["Mesa 1", "Mesa 2"]

document = "Gestión-Buho-bar"
sheet = "Reservas"
credentials = st.secrets["google"]["credentials_google"]
idcalendar = "5421f66156b07eb8c0bbabe15cc57e42274cac03d7eda8060c4dca808e195478@group.calendar.google.com"
idcalendar2 = "48c588c5ede47244d59f8bbdd64de725838b7ca28bf73839f37a6b950992aff8@group.calendar.google.com"
time_zone = "America/La_Paz"

##FUNCIONES
def generate_uid():
    return str(uuid.uuid4())

def add_hour_and_half(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    new_time = (dt.datetime.combine(dt.date.today(),parsed_time) + dt.timedelta(hours=6)).time()
    return new_time.strftime("%H:%M")

st.set_page_config(page_title, page_icon, layout=layout)

st.image("assets/TT.png")
st.title("Buho Bar Reservas")
st.text("Reserva tu mesa")

selected = option_menu(menu_title=None, options=["Reservar","Galeria"], 
            icons=["calendar-date","bookmarks"], 
            orientation="horizontal")

if selected == "Reservar":

    st.subheader("Reservar")

    c1,c2 = st.columns(2)

    nombre = c1.text_input("Tu nombre")
    mail = c2.text_input("Tu mail")
    fecha = c1.date_input("Fecha")
    pista = c1.selectbox("Mesas",pistas)
    if fecha:
        if pista == "Mesa 1":
            id = idcalendar
        if pista == "Mesa 2":
            id = idcalendar2
        calendar = GoogleCalendar(credentials, id)
        hours_blocked = calendar.get_events_star_time(str(fecha))
        result_hours = np.setdiff1d(horas, hours_blocked)
    hora = c2.selectbox("Hora",result_hours)
    
    notas = c2.text_input("Notas")

    enviar = st.button("Reservar")

##BACKEND
    if enviar:

        with st.spinner("Cargando..."):
            if nombre == "":
                st.warning("El nombre es obligatorio")
            elif mail == "":
                st.warning("El email es obligatorio")
            elif fecha == "":
                st.warning("El email es obligatorio")
            elif hora == "":
                st.warning("El email es obligatorio")
            elif pista == "":
                st.warning("El email es obligatorio")
            elif notas == "":
                st.warning("El email es obligatorio")
            else:
                #Crear evento en google calendar
                parsed_time = dt.datetime.strptime(hora, "%H:%M").time()
                hours1 = parsed_time.hour                
                minutes1 = parsed_time.minute                
                end_hours = add_hour_and_half(hora)
                parsed_time2 = dt.datetime.strptime(hora, "%H:%M").time()
                hours2 = parsed_time2.hour                
                minutes2 = parsed_time2.minute                
                start_time = dt.datetime(fecha.year,fecha.month,fecha.day, hours1, minutes1).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S-00:00')                
                end_time = dt.datetime(fecha.year,fecha.month,fecha.day, hours2, minutes2).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S-00:00')
                calendar = GoogleCalendar(credentials, id)
                calendar.create_event(nombre, start_time, end_time, time_zone )
                #Registro google sheet
                uid = generate_uid()
                data = [[nombre,mail,str(fecha),hora,pista,notas,uid]]
                gs = GoogleSheets(credentials,document,sheet)
                range = gs.get_last_row_range()
                gs.write_data(range,data)


                st.success("Su Mesa ha sido reservada de forma exitosa")


