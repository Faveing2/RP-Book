import epd
from machine import Pin
import os
import time
import settings

BUTTON0_PIN = 2
BUTTON1_PIN = 3
BUTTON2_PIN = 4

CONFIGPATH = "settings.json"

LINES = 10
LINEWIDTH= 31

bookDIR = "books/"
books = os.listdir(bookDIR)

config = settings.settings(CONFIGPATH)

config.data["books"] = books
config.save()

display = epd.EPD_2in13_B_V4_Landscape()
#test_screen(display)

button_0 = Pin(BUTTON0_PIN, Pin.IN, Pin.PULL_UP)
button_1 = Pin(BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
button_2 = Pin(BUTTON2_PIN, Pin.IN, Pin.PULL_UP)

def display_page(current_page, book, total_pages):

    print("displaying page", current_page)

    display.imageblack.fill(0xff)
    with open(bookDIR+book,"r") as file:
        i = 0
        file.seek(LINEWIDTH*LINES*(current_page))
        while i < LINES:
            line = file.read(LINEWIDTH)
            #clean = ''.join(c for c in line if c.isprintable() or c in '\n\r\t')
            clean = ""

            for c in line:
                code = ord(c)

                # Keep printable ASCII plus newlines
                if code >= 32 and code < 127:
                    clean += c

            display.imageblack.text(clean, 0,10*(i+2), 0x00)

            #print(line)
            i += 1
        
    display.imageblack.text("Page:"+str(current_page)+"/"+str(total_pages), 0,120,0x00)
    display.imageblack.hline(0,17,250,0x00)
    display.imageblack.text(book,0,8,0x00)
    display.display()

    #print(page_data)


def reading_mode(book_index,book):
    print("Reading", book)

    total_size = os.stat(bookDIR+book)[6]
    total_pages = int(total_size/LINEWIDTH*LINES)-1

    ### Load current page
    current_page = 0 

    if book not in config.data["current_pages"]:
        config.data["current_pages"][book] = 0
        print("Created new entry for book")
    else:
        current_page = config.data["current_pages"][book]
        print("Using existing entry for book")

    print("Current_page", current_page)

    display_page(current_page, book,total_pages)

    while True:
        #print(button_0.value())
        if button_0.value() == 0:
            if current_page == 0:
                continue
            else:
                current_page -= 1
                config.data["current_pages"][book] = current_page
                config.save()
                display_page(current_page, book,total_pages)

        if button_1.value() == 0:
            config.data["current_book"] = ""
            config.save()
            bookSelectionMenu()

        if button_2.value() == 0:
            if current_page == total_pages:
                continue
            else:
                current_page += 1
                config.data["current_pages"][book] = current_page
                config.save()
                display_page(current_page, book,total_pages)

        time.sleep(0.05)

def display_book_selection(display, current_selection:int, books):

    #display.Clear(0xff, 0xff)
    display.imageblack.fill(0xff)

    for index, book in enumerate(books):

        if current_selection == index:
            display.imageblack.rect(0,10*(index+1),8,8,0x00, True)
        else:
            display.imageblack.rect(0,10*(index+1),8,8,0x00)

        display.imageblack.text(book, 10, 10*(index+1), 0x00)

    display.display()

def bookSelectionMenu():
    
    selected_book = 0

    display_book_selection(display, selected_book, config.data["books"])

    while True:
        #print(button_0.value())
        if button_0.value() == 0:
            if selected_book == 0:
                continue
            else:
                selected_book -= 1
                display_book_selection(display, selected_book, config.data["books"])
        if button_1.value() == 0:
            config.data["current_book"] = config.data["books"][selected_book]
            config.save()
            print("Selected_book", config.data["current_book"])
            reading_mode(selected_book,config.data["current_book"])

        if button_2.value() == 0:
            if selected_book == len(books)-1:
                continue
            else:
                selected_book += 1
                display_book_selection(display, selected_book, config.data["books"])

        time.sleep(0.05)

if config.data["current_book"] == "":
    bookSelectionMenu()
else:
    reading_mode(config.data["books"].index(config.data["current_book"]),config.data["current_book"])
    pass

# def render_page(display, text):
#     display.imageblack.text(text, 0, 10, 0x00)
#     display.display()

# def test_screen(display):
#     display.Clear(0xff, 0xff)

#     display.imageblack.fill(0xff)
#     display.imageblack.text("RP-BOOK", 0, 10, 0x00)
#     display.imageblack.text("Unicode text rendering:",0,20,0x00)
#     display.imageblack.text("だいすき", 180, 20, 0x00)
#     display.display()

# def display_text_partial(display, text, x, y, color):
#     display.imageblack.text(text, x, y, color)


# display = epd.EPD_2in13_B_V4_Landscape()
# #test_screen(display)

# button_0 = Pin(BUTTON0_PIN, Pin.IN, Pin.PULL_UP)
# button_1 = Pin(BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
# button_2 = Pin(BUTTON2_PIN, Pin.IN, Pin.PULL_UP)

# book_data = None

# # with open(bookDIR, "r") as file:
# #     book_data = file.read()
# #     file.close()

# #render_page(display, book_data)

# while True:
#     #print(button_0.value())
#     if button_0.value() == 0:
#         test_screen(display)
#     if button_1.value() == 0:
#         test_screen(display)
#     if button_2.value() == 0:
#         test_screen(display)
    
#     time.sleep(0.05)