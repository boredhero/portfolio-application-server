import json
import yaml
import os

from yaml.error import YAMLError

class SimpleJsonYmlReader:


    def __init__(self, filepath):

        if filepath is not None:
            self.FILETYPES = [".json", ".yml", ".JSON", ".YML", ".yaml", ".YAML"]
            self.YML = [".yml", ".YML", ".yaml", ".YAML"]
            self.JSON = [".json", ".JSON"]
            self.__filepath = filepath
            self.__ext = self.__get_file_extension(filepath)
        else:
            print("SimpleJsonYmlReader: Error: Filepath was None")

    def __get_file_extension(self, filepath):
        root,ext = os.path.splitext(filepath)
        if ext in ['.gz', '.bz2']:
            ext = os.path.splitext(root)[1] + ext
        return ext

    def read_file(self):
        """
        Read JSON/YML into a dict
        
        :returns dict filedict: File contents
        """
        file = None
        if self.__ext in self.FILETYPES:
            try:
                with open(self.__filepath) as f:
                    if self.__ext in self.YML:
                        file = yaml.load(f, Loader=yaml.FullLoader)
                    elif self.__ext in self.JSON:
                        file = json.load(f)
                    else:
                        print("SimpleJsonYmlReader: read_file: Error: Filetype not JSON or YAML. Please check your fileextension")
            except FileNotFoundError as e:
                print(f"SimpleJsonYmlReader: read_file: File not found: {self.__filepath}\n", e)
            except json.JSONDecodeError as e:
                print(f"SimpleJsonYmlReader: read_file: Error decoding JSON file: {self.__filepath}\n", e)
            except yaml.YAMLError as e:
                print(f"SimpleJsonYmlReader: read_file: Error decoding YML file {self.__filepath}\n", e)
            except Exception as e:
                print(f"SimpleJsonYmlReader: read_file: An unknown error occured proccessing the file {self.__filepath}\n", e)
        else:
            print(f"SimpleJsonYmlReader: read_file: Error: File extension {self.__ext} not a valid extension!")
        return file