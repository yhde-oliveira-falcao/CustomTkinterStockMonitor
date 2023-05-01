import threading
from tkinter import *
from tkinter import messagebox
import requests as requests
import time
from twilio.rest import Client

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
                        from_="+16477993157",
                        to="+16478353811"
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
        window.after(3000, check_running, ticker, target)


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


if __name__ == '__main__':
    window = Tk()
    window.title("Stock Price Monitor")
    window.config(padx=100, pady=100)

    # Labels
    stock_label = Label(text="Stock:")
    stock_label.grid(row=1, column=0)

    target_label = Label(text="Target Price")
    target_label.grid(row=1, column=1)

    # Entries
    stock_name_entry = Entry(width=10)
    stock_name_entry.grid(row=2, column=0, columnspan=1)
    stock_name_entry.focus()

    target_price_entry = Entry(width=10)
    target_price_entry.grid(row=2, column=1, columnspan=1)
    target_price_entry.focus()

    # Buttons
    add_button = Button(text="Monitor", width=10,
                        command=monitor)  # command=save (to call the function save ==line 7 on my github tutorial
    add_button.grid(row=4, column=0, columnspan=2)

    add_button = Button(text="End Monitor", width=10, command=end_monitor)
    add_button.grid(row=6, column=0, columnspan=2)

    window.mainloop()
