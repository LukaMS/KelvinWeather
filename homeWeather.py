#Import a ton of libraries, some might not even be used
from tkinter import *
from tkinter import ttk
import requests
import json
import datetime
from PIL import ImageTk, Image
import csv
import pandas as pd
import time
import customtkinter as ct
import tkintermapview
from geopy.geocoders import Nominatim
import mysql.connector
#GLobal Variables that are used during the inizialization of all the pages I think
update = False
old_city = 'asq'
countryThing = ''
geolocator = Nominatim(user_agent="homeWeather")
locationNew = geolocator.geocode('Toronto')

#Weather App Iniziatlization
class weatherApp(Tk):

    def __init__(self, *args, **kwargs):

        Tk.__init__(self, *args, **kwargs)

        #Create conatiner
        container = Frame(self, bg='white')
        container.grid(row=0,column=0)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        #Create Frames for each Page in App
        for F in (homePage,Page1):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

        #Show Home Page On Open
        self.show_frame(homePage)
    #Function to Change frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class userPage(Frame):
    def __init__(self, parent, controller):

        Frame.__init__(self, parent, bg='white')

        user_id = 2
        dob = '2003-02-03'
        firstnameBox = ct.CTkEntry(self)
        firstnameBox.grid(row=1, column=1, padx = 10, pady = 10)
        lastnameBox = ct.CTkEntry(self)
        lastnameBox.grid(row=2, column=1, padx = 10, pady = 10)
        def createuser():
            query = "INSERT INTO users VALUES ("+str(user_id)+", '"+firstnameBox.get()+"', '"+lastnameBox.get()+"', '"+dob+"')"
            execute_query(connection, query)
        goButton = ct.CTkButton(self, text = 'GO!', command = lambda : [createuser()])
        goButton.grid(row=3, column=1)


#Home Page Iniziatlization
class homePage(Frame):
    def __init__(self, parent, controller):
        #Global Variables, yes its very messy
        global countryThing, countryBox, countries, cities_list, cityBox, CountryEntry, locationNew, map_widget2, logoImage

        #Iniitialize Fram
        Frame.__init__(self, parent, bg='white')

        #From City CSV get a list of all countries in the world
        colnames = ['name','country','subcountry', 'geonameid']
        data = pd.read_csv('/Users/lukam/python/world-cities_csv.csv', encoding='utf8', names=colnames, skiprows=(0,))
        countries = []
        for row in data['country']:
            if row in countries:
                pass
            else:
                countries.append(row)

        #Based on the Country selesct, Update the list of cities on the weather Page
        def updateCityGlobal(data):
            citydata = []
            index = countries.index(data)
            for list in cities_list:
                if cities_list.index(list) == index:
                    for thing in list:
                        citydata.append(thing)
                    break
            cityBox.delete(0,'end')
            for item in citydata:
                cityBox.insert('end', item)

        #When User left clicks on the map, get the country they clicked and put it into the entry box
        def left_click_event(coords):
            location = geolocator.reverse(str(coords[0])+','+str(coords[1]), language='en')
            address = location.raw['address']
            country = address.get('country', '')
            countryEntry.delete(0,'end')
            countryEntry.insert(0,country)
            countryBox.delete(0,'end')
            countryBox.insert('end',country)
            map_widget.delete_all_marker()
            marker = map_widget.set_marker(coords[0],coords[1])

        #If a country in the list box if clicked put it into the entry box
        def filloutGlobal(event):
            countryEntry.delete(0,END)
            countryEntry.insert(0, countryBox.get(ACTIVE))

        #Update the country entry box
        def updateCheckGlobal(data):
            countryBox.delete(0,'end')
            for item in data:
                countryBox.insert('end', item)

        #Check the value in the entry box on key release, update the country list and call updateCheckGlobal
        def checkkeyGlobal(event):
            value = event.widget.get()
            print(value)

            if value == '':
                countrydata = countries
            else:
                countrydata = []
                for item in countries:
                    if value.lower() in item.lower():
                        countrydata.append(item)

            updateCheckGlobal(countrydata)

        #This function does a mash of things, it grabs the current country and puts it in a global variable
        #for the next page. It updates the the Coordinatesof the location and changes the set position of the
        #map on the next page, it also gets rid of the logo
        def getCountry():
            global countryThing, skyImage, location
            countryThing = countryEntry.get()
            locationNew = geolocator.geocode(countryThing)
            map_widget2.set_position(locationNew.latitude, locationNew.longitude)
            skyImage.place(x=300,y=100)
            logoImage.grid_forget()

        #When return key press, run functions to get weather page set up
        def return_pressed(event):
            getCountry()
            controller.show_frame(Page1)
            updateCityGlobal(countryEntry.get())
            updateCheckGlobal(countryEntry.get())


        #Logo image
        image4 = Image.open('/Users/lukam/python/300LogoCopy.png')
        image4 = image4.resize((300,83), Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(image4)

        #PLace logo image and keep a reference
        logoImage = Label(image=logo, bg='white')
        logoImage.image = logo
        #logoImage.grid(row=0,column=0, sticky=W+N, columnspan=3, padx = 10, pady=10)

        #Create map widget
        map_widget = tkintermapview.TkinterMapView(self, width=400, height=400, corner_radius = 5)
        map_widget.grid(row=3, column=0, columnspan=3, padx=10)
        map_widget.set_position(43.6532, -79.3832)
        map_widget.set_zoom(7)
        map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        map_widget.add_left_click_map_command(left_click_event)

        #Add a weather button, acts as an enter button
        logoPurple = '#6936F5'
        button1 = ct.CTkButton(self, text ="WEATHER!", corner_radius=5, fg_color = logoPurple,
        command = lambda : [getCountry(),controller.show_frame(Page1), updateCheckGlobal(countryEntry.get()), updateCityGlobal(countryEntry.get())])

        button1.grid(row = 1, column = 1, padx = 10, pady = (100,0))

        #Country Entry Box that is binded to key release and enter key
        countryEntry = ct.CTkEntry(self,corner_radius=5, fg_color='white', text_color='Black')
        countryEntry.grid(row=1,column=2,sticky=W, pady=(100,0))
        countryEntry.bind('<KeyRelease>', checkkeyGlobal)
        countryEntry.bind('<Return>', return_pressed)

        #Scrollbar for the country list box
        scrollbarCountry = ct.CTkScrollbar(self, height = 175)
        scrollbarCountry.grid(row=2,column=2,sticky=W)

        #country list box
        countryBox = Listbox(self, yscrollcommand=scrollbarCountry.set)
        countryBox.grid(row=2, column=2,sticky=W,padx=15)
        countryBox.bind('<<ListboxSelect>>', filloutGlobal)
        scrollbarCountry.configure(command=countryBox.yview)

        #Call function on startup to populate the country list box with all countries
        updateCheckGlobal(countries)
#Main Weather page
class Page1(Frame):

    def __init__(self, parent, controller):
        #Mish Mash of global varibales again, might deal with them someday
        global countryThing, countryBox, countries, cities_list, cityBox, skyImage, locationNew, map_widget2, logoImage
        Frame.__init__(self, parent, bg='white')
        #Purple That matches logo
        logoPurple = '#6936F5'
        #API key for weather data
        api_key = '093f37f2719809109d4a2bb80842450b'

        #city entry box
        city_name = StringVar()
        city_entry = Entry(self, textvariable=city_name, width=10)
        city_entry.grid(row=1,column=0, ipady=1, stick=W+E+N+S)

        #Create a list of the all the cities in the world by going through each line of the CSV
        cities_list = []
        with open('/Users/lukam/python/world-cities_csv.csv', encoding='utf8') as data2:
            datathing = csv.reader(data2)

            for i in range(len(countries)):
                temp_list = []
                line_count = 0
                for row in datathing:
                    if line_count == 0:
                        pass
                    else:
                        if row[1] == countries[i]:
                            temp_list.append(row[0])
                        else:
                            break
                    line_count +=1
                cities_list.append(temp_list)

        """ALL THE FUNCTIONS!"""
        #Functrion to get rid of the sun/moon icon and move it to a place where u can't see it
        def move_pic():
            global skyImage
            skyImage.configure(image='')
            skyImage.place(x=500,y=300)
            logoImage.grid(row=0,column=0, sticky=W+N, columnspan=3, padx = 10, pady=10)
        #Check value of city entry box on key release and update list of cities acordingly
        def checkkeyCity(event):
            index = countries.index(countryThing)
            value = event.widget.get()
            print(value)
            citydata = []
            for list in cities_list:
                if cities_list.index(list) == index:
                    for thing in list:
                        if value.lower() in thing.lower():
                            citydata.append(thing)
            updateCheck(citydata)

        #Update the values in the city list box
        def updateCheck(data):
            cityBox.delete(0,'end')

            for item in data:
                cityBox.insert('end', item)

        #Fillout the city entry box when item is selected from list box
        def filloutCity(event):
            city_entry.delete(0,END)

            city_entry.insert(0, cityBox.get(ACTIVE))

        #Check the sunset time in the selected city and change image to sun or moon
        def check_image(api):
            sys = api['sys']
            sunsetTime = datetime.datetime.fromtimestamp(sys['sunset'])
            time = datetime.datetime.fromtimestamp(api['dt'])
            if (time > sunsetTime):
                skyImage.configure(image=moon)
            else:
                skyImage.configure(image=sun)

        #Get all information from an api reqeuest using city in city entry box, assing values to cooresponding variables
        def city_name():
            global update, old_city
            if update == True:
                api_requests = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + old_city + '&appid=' + api_key)
            else:
                api_requests = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + city_entry.get() + '&appid=' + api_key)
                old_city = city_entry.get()
            api = json.loads(api_requests.content)
            if api['cod'] == '404' or city_entry.get() == '':
                pass
            else:
                check_image(api)
                main = api['main']
                current_temprature = main['temp']
                humidity = main['humidity']
                tempmin = main['temp_min']
                tempmax = main['temp_max']

                coord = api['coord']
                longtitude = coord['lon']
                latitude = coord['lat']

                sys = api['sys']
                country = sys['country']
                city = api['name']

                lable_temp.configure(text=current_temprature)
                lable_humidity.configure(text=humidity)
                max_temp.configure(text=tempmax)
                min_temp.configure(text=tempmin)
                lable_lon.configure(text=round(longtitude,2))
                lable_lat.configure(text=round(latitude,2))
                lable_country.configure(text=country)
                lable_city.configure(text=city)

        #Refresh the time and weather data
        def refresh():
            global update
            update = True
            city_name()
            update = False
            dt = datetime.datetime.now()
            hour.configure(text = dt.strftime('%I : %M %p'))

        def left_click_event(coords):
            location = geolocator.reverse(str(coords[0])+','+str(coords[1]), language='en')
            address = location.raw['address']
            countryMap = address.get('city', '')
            city_entry.delete(0,'end')
            city_entry.insert(0,countryMap)
            cityBox.delete(0,'end')
            cityBox.insert('end',countryMap)
            map_widget2.delete_all_marker()
            marker = map_widget2.set_marker(coords[0],coords[1])
        def reset_countryBox():
            countryBox.delete(0,'end')
            countryBox.insert(0, countryThing)

        """ALL THE LABELS AND WIDGETS!"""
        #Set data and time
        dt = datetime.datetime.now()
        date = Label(self, text=dt.strftime('%A--'), bg='white', font=("bold", 15))
        date.grid(row=2,column=2,sticky=W)
        month = Label(self, text=dt.strftime('%m %B'), bg='white', font=("bold", 15))
        month.grid(row=2, column=3, sticky=W)
        hour = Label(self, text = dt.strftime('%I : %M %p'), bg='white', font=('bold', 15))
        hour.grid(row=3,column=2)


        #Create second smaller map for weather page
        map_widget2 = tkintermapview.TkinterMapView(self, width=200, height=200, corner_radius = 5)
        map_widget2.grid(row=8, column=2, columnspan=3)
        map_widget2.set_zoom(3)
        map_widget2.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        map_widget2.add_left_click_map_command(left_click_event)

        # Button to go back to home page
        homeButton = ct.CTkButton(self, text ="Home", width = 15, fg_color=logoPurple, corner_radius=5,
                            command = lambda : [controller.show_frame(homePage), move_pic(), reset_countryBox()])
        homeButton.grid(row = 1, column = 3, sticky=W)

        # Button to search city
        city_nameButton = ct.CTkButton(self, text="Search", command=city_name, width= 15, fg_color=logoPurple,
                            corner_radius=5)
        city_nameButton.grid(row=1, column=1, padx=5, stick=W)


        # Country  Names and Coordinates
        lable_city = Label(self, text="...", width=0, bg='white', font=("bold", 15))
        lable_city.grid(row=2,column=0,pady=5)

        #Country Label
        lable_country = Label(self, text="...", width=0, bg='white', font=("bold", 15))
        lable_country.grid(row=2,column=1,pady=5)

        #Longitude Label
        lable_lon = Label(self, text="...", width=0, bg='white', font=("Helvetica", 15))
        lable_lon.grid(row=3,column=0,pady=5)

        #Latitude Label
        lable_lat = Label(self, text="...", width=0, bg='white', font=("Helvetica", 15))
        lable_lat.grid(row=3,column=0,pady=5,sticky=E)

        # Current Temperature
        lable_temp = Label(self, text="...", width=0, bg='white', font=("Helvetica", 50), fg='black')
        lable_temp.grid(row=4, column = 0, pady=5)

        # Other temperature details
        #Humidity
        humi = Label(self, text="Humidity: ", width=0, bg='white', font=("bold", 15))
        humi.grid(row=5, column = 0,pady=5, sticky=W)

        lable_humidity = Label(self, text="...", width=0, bg='white', font=("bold", 15))
        lable_humidity.grid(row=5, column=0,pady=5, sticky=E)

        #Max Temp
        maxi = Label(self, text="Max. Temp.: ", width=0, bg='white', font=("bold", 15))
        maxi.grid(row=6, column=0,pady=5,stick=W)

        max_temp = Label(self, text="...", width=0, bg='white', font=("bold", 15))
        max_temp.grid(row=6, column=0,pady=5,sticky=E)

        #Min Temp
        mini = Label(self, text="Min. Temp.: ", width=0, bg='white', font=("bold", 15))
        mini.grid(row=7, column=0,pady=5,sticky=W)

        min_temp = Label(self, text="...", width=0, bg='white', font=("bold", 15))
        min_temp.grid(row=7, column=0,pady=5,sticky=E)

        #Refresh Button
        refresh_button = ct.CTkButton(self, text="Refresh", command=refresh, width=80, fg_color=logoPurple, corner_radius = 5)
        refresh_button.grid(row=1, column=2, padx=5, stick=W)

        #Images
        image1 = Image.open('/Users/lukam/python/moon.jpg')
        image1 = image1.resize((100,100), Image.ANTIALIAS)
        moon = ImageTk.PhotoImage(image1)

        image2 = Image.open('/Users/lukam/python/sun.jpg')
        image2 = image2.resize((100,100), Image.ANTIALIAS)
        sun = ImageTk.PhotoImage(image2)

        skyImage = Label(image='', bg = 'white')

        #Scroll bar for city listbox
        scrollbarCity = ct.CTkScrollbar(self)
        scrollbarCity.grid(row=8,column=1,sticky=W,pady=20)

        #City list box
        cityBox = Listbox(self, relief = SUNKEN, bd = 3, font=('Arial', 10), width = 30, yscrollcommand = scrollbarCity.set)
        cityBox.grid(row=8,column=0)

        #Binds for city entry and list box
        cityBox.bind('<<ListboxSelect>>', filloutCity)
        city_entry.bind('<KeyRelease>', checkkeyCity)

        #Config scrol bar for list box
        scrollbarCity.configure(command=cityBox.yview)

#Create and config app
app = weatherApp()
app.geometry('520x720')
app.configure(bg='white')
app.title('Kelvin Weather')
app.mainloop()
