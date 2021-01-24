# Jan Proniewicz, 297989, Informatyka - Data Science
""" Funkcje, operujące na plikach .json, tj. pobranie zawartości lub zapisanie danych do odpowiedniego pliku """
import json


def get_data_from_json(json_file_name):
    """ Pobranie zawartości z wybranego pliku .json (json_file_name) """
    with open(json_file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def set_data_to_json(json_file_name, data_to_set):
    """ Zapisanie danych (data_to_set) do wybranefo pliku .json (json_file_name) """
    with open(json_file_name, "w", encoding="utf-8") as f:
        json.dump(data_to_set, f, indent=4, ensure_ascii=False)
