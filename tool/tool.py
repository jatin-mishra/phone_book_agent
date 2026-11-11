
from abc import ABC, abstractmethod
import json

class Tool(ABC):

    @abstractmethod
    def get_schema(self) -> dict: 
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def execute(self, input: dict) -> dict:
        pass

    def error(self, message, how_to_fix) -> dict:
        return {
            "status" : "error",
            "error" : message,
            "how_to_fix" : how_to_fix
        }
            


class GetPersonsPhoneNumber(Tool):

    def __init__(self):
        super().__init__()
        self.directory = {
            "jatin" : "111111",
            "suresh" : "222222",
            "mukesh" : "333333",
            "deepak" : "4444444",
            "priyanka" : "555555"        
        }
        self.path = "schema/get_phone_number.json"
        self.schema = self._read_json()

    def _read_json(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_name(self):
        return self.schema.get("name")

    def get_schema(self):
        return self.schema

    async def execute(self, input: dict) -> dict:
        if "name" not in input or input["name"] not in self.directory:
            return self.error("Invalid name", f"people names in directory : {list(self.directory.keys())}")
        
        return {
            "phone_number" : self.directory.get(input["name"])
        }