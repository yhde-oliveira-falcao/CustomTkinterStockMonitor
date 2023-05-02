import tkinter
from tkinter import messagebox

import customtkinter
from PIL import Image, ImageTk

import requests as requests
import time

from customtkinter import CTkEntry, CTkButton
from twilio.rest import Client
import threading


STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = ""
NEWS_API_KEY = ""

TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""

# Declare a global variable to control the ON and OFF of the program. (Declare False to stop running)
running = True

# locks the thread to run a instance until the instance is over (finished or flagged off
lock = threading.Lock()

def test_update_price(ticker, target):
    global running
    with lock:  # locks the thread to run this instance until the end before the function is called again with
        # another parameter
        while running:
            print(f"Ticker: {ticker}, Target: {target}")
            time.sleep(3)  # with threading.lock it works fairly precise and with almost no variances in times


def update_price(ticker, target):
    global running
    with lock:
        stock_params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",  # fix this to get the desired time
            "symbol": ticker,
            # "outputsize":"full",
            # "interval": "60min",
            "apikey": STOCK_API_KEY,
        }
        while running:
            response = requests.get(STOCK_ENDPOINT, params=stock_params)
            data = response.json()["Time Series (Daily)"]
            data_list = [value for (key, value) in data.items()]
            yesterday_data = data_list[0]
            day_before_yesterday_data = data_list[1]

            yesterday_closing_price = yesterday_data["4. close"]
            day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

            print(yesterday_closing_price)
            difference = float(yesterday_closing_price) - float(
                day_before_yesterday_closing_price)  # wrap everything in abs() to get the positive (absolute) value
            print(difference)

            diff_percentage = (difference / float(yesterday_closing_price)) * 100
            print(diff_percentage)

            if diff_percentage > 5 or diff_percentage < -5:  # check if the variation is greater than expected
                news_params = {
                    "apiKey": NEWS_API_KEY,
                    "qInTitle": ticker,
                }
                news_response = requests.get(NEWS_ENDPOINT, params=news_params)
                articles = news_response.json()["articles"]
                two_articles = articles[:2]

                formatted_articles = [
                    f"{ticker}: {diff_percentage}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for
                    article in two_articles]
                client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

                for article in formatted_articles:
                    client.messages.create(
                        body=article,
                        from_="+",
                        to="+"
                    )
            #time.sleep(86400)
            time.sleep(5)

def end_monitor():
    global running
    running = False
    messagebox.showinfo(title="Monitor Ended", message="The monitor has finished")


def check_running(ticker, target):
    if running:
        # update_price(ticker, target)
        threading.Thread(target=update_price, args=(ticker, target)).start()
        app.after(3000, check_running, ticker, target)


def monitor():  # running in the main thread (same as GUI
    global running
    ticker = stock_name_entry.get()
    target = target_price_entry.get()

    if len(ticker) == 0:
        messagebox.showinfo(title="Error", message="Input Ticker")
    elif len(target) == 0:
        messagebox.showinfo(title="Error", message="Input target price")
    else:
        is_valid = messagebox.askokcancel(title=ticker,
                                          message=f"Monitor the stock: {ticker} \nat the price: {target}?") # gets
        # the "OK of the user to start the monitoring

        if is_valid:
            running = True
            check_running(ticker, target)



# GUI SETTING ==========================================================

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("500x400")
app.title("Ola Mundo")

# Open and resize the image
image = Image.open("logo.png")
image = image.resize((120, 50))

# Convert the image to a Tkinter PhotoImage object
photo = ImageTk.PhotoImage(image)

# def button_callback():
# label_2.configure(text="Pythonista, Olá Mundo")


frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=20, padx=60, fill="both", expand=True)

sub_frame1 = customtkinter.CTkFrame(master=frame_1, width=20, height=20)
sub_frame1.grid(row=0, column=0, pady=5, padx=5, sticky="")
sub_frame1.configure(width=100, height=50)

# Create a label to display the image
label = customtkinter.CTkLabel(sub_frame1, image=photo, text="")
label.grid()

label_1 = customtkinter.CTkLabel(master=frame_1, text="Monitor de Ações da Bolsa", justify=customtkinter.CENTER, font=("TkDefaultFont", 16, "bold"))
label_1.place(relx=0.5, rely=0.25, anchor=tkinter.CENTER)

# Entries and Buttons
stock_label = customtkinter.CTkLabel(master=frame_1, text="Stock")
stock_label.place(relx=0.3, rely=0.4, anchor=tkinter.CENTER)

stock_name_entry = customtkinter.CTkEntry(master=frame_1)
stock_name_entry.place(relx=0.3, rely=0.5, anchor=tkinter.CENTER)

target_label = customtkinter.CTkLabel(master=frame_1, text="Target")
target_label.place(relx=0.7, rely=0.4, anchor=tkinter.CENTER)

target_price_entry = customtkinter.CTkEntry(master=frame_1)
target_price_entry.place(relx=0.7, rely=0.5, anchor=tkinter.CENTER)

submit_button = customtkinter.CTkButton(master=frame_1, text="Monitor", command=monitor)
submit_button.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)

end_monitor_button = customtkinter.CTkButton(master=frame_1, text="End Monitor", command=end_monitor)
end_monitor_button.place(relx=0.5, rely=0.9, anchor=tkinter.CENTER)

app.mainloop()
