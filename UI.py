import customtkinter
from geopy.geocoders import Nominatim
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.title("Gruppe A Python eksamen")
app.geometry("1000x600")
app.eval('tk::PlaceWindow . center')

app.grid_columnconfigure(0, weight=0)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

app.frame_left = customtkinter.CTkFrame(master=app, width=150, corner_radius=0, fg_color=None)
app.frame_left.grid(row=0, column=0, pady=0, padx=10, sticky='nsew')
app.frame_left.grid_rowconfigure(2, weight=1)

label= customtkinter.CTkLabel(master=app.frame_left, text='Calculate price', font=('Roboto',24))
label.pack(pady=12, padx=10)

entry_address = customtkinter.CTkEntry(master=app.frame_left, placeholder_text='Address')
entry_address.pack(pady=12, padx=10)

entry_zip_code = customtkinter.CTkOptionMenu(app.frame_left, values=['Choose Zip','2800','2820','2830','2840','2850','2900','2920','2930','2942','2950','3000','3460'])
entry_zip_code.pack(pady=12, padx=10)

entry_size = customtkinter.CTkEntry(master=app.frame_left, placeholder_text='Size')
entry_size.pack(pady=12, padx=10)

entry_type = customtkinter.CTkOptionMenu(app.frame_left, values=['Choose Type','Villa','Ejerlejlighed','Rækkehus','Villalejlighed'])
entry_type.pack(pady=12, padx=10)

entry_energy_class = customtkinter.CTkOptionMenu(app.frame_left, values=['Choose Energy class','A2020','A2015','A2010','B','C','D','E','F','G'])
entry_energy_class.pack(pady=12, padx=10)

app.frame_right = customtkinter.CTkFrame(master=app, corner_radius=0)
app.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky='nsew')


label= customtkinter.CTkLabel(master=app.frame_right, text='Map', font=('Roboto',24))
label.pack(pady=12, padx=10)

def load_model():
    global model
    model = joblib.load('RFG_Model')
    return model

def get_coordinates(address, postnr):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(f'{address} {postnr} Danmark')
    if location is not None:
        x = location.latitude
        y = location.longitude
    else:
        x = None
        y = None

    return x, y

def calculate():
    address = entry_address.get()
    zip_code = entry_zip_code.get()
    size = entry_size.get()
    type = entry_type.get()
    energy_class = entry_energy_class.get()

    if address is None:
        return
    if zip_code == "Choose Zip":
        return
    if type == "Choose Type":
        return
    if size is None:
        return
    if energy_class == "Choose Energy Class":
        return

    x,y = get_coordinates(address, zip_code)
    
    model = load_model()

    if model:
        cities = ['2800', '2820', '2830', '2840', '2850', '2900', '2920', '2930', '2942', '2950', '3000', '3460']
        dataframes = []

        for city in cities:
            filename = f'./data/house_data/house_data_{city}.csv'
            df = pd.read_csv(filename)
            dataframes.append(df)

        data = pd.concat(dataframes, ignore_index=True)
        data.dropna(inplace=True)

        features = ['X', 'Y', 'Size', 'Type', 'Energy class']
        label_encoders = {}
        for feature in features:
            if data[feature].dtype == 'object':
                label_encoders[feature] = LabelEncoder()
                data[feature] = label_encoders[feature].fit_transform(data[feature])
        
        new_house = pd.DataFrame([[x, y, size, type, energy_class]], columns=features)
        for feature in features:
            if new_house[feature].dtype == 'object':
                new_house[feature] = label_encoders[feature].transform(new_house[feature])
        prediction = model.predict(new_house)
        print(prediction)
    

# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=app.frame_left, text="Calculate", command=calculate)
button.pack(pady=12, padx=10)

def change_map(app, new_map):
    if new_map == "OpenStreetMap":
        app.map_widget.set_tile_server("https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png%22")
    elif new_map == "Google normal":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D&s=Ga", max_zoom=22)
    elif new_map == "Google satellite":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x=%7Bx%7D&y=%7By%7D&z=%7Bz%7D&s=Ga", max_zoom=22)

def change_appearance_mode(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)

app.map_option_menu = customtkinter.CTkOptionMenu(app.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=change_map)
app.map_option_menu.pack(pady=12, padx=10)

app.appearance_mode_label = customtkinter.CTkLabel(app.frame_left, text="Appearance Mode:", anchor="w")
app.appearance_mode_label.pack(pady=12, padx=10)
app.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(app.frame_left, values=["Light", "Dark", "System"],
                                                                       command=change_appearance_mode)
app.appearance_mode_optionmenu.pack(pady=12, padx=10)

#app.map_widget.set_address('Nordsjælland')
app.map_option_menu.set('Google normal')
app.appearance_mode_optionmenu.set('Dark')

app.mainloop()