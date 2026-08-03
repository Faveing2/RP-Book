import json

class settings():

    def __init__(self, filepath) -> None:
        self.filepath = filepath
        with open(self.filepath, "r") as file:
            self.data = json.load(file)
        
        print("Loaded settings")

    def setCurrentPage(self,current_book:str, current_page:int):
        pass

    def getCurrentBook(self):
        return self.data["current_book"]

    def save(self):
        with open(self.filepath,"w") as file:
            json.dump(self.data, file)

        print("Saved settings")