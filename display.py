from epd import EPD_2in13_B_V4_Landscape

class display(EPD_2in13_B_V4_Landscape):

    def __init__(self):
        super().__init__()

    def display_line(self):
        pass

    def display_image(self):
        pass

    def display_progress_bar(self, current_page, total_pages):
        pass
    
    def update_screen(self):
        self.display()