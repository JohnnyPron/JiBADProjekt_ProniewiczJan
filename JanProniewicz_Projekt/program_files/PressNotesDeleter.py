# Jan Proniewicz, 297989, Informatyka - Data Science
""" Funkcja systemu, której zadaniem jest usuwanie 'starych' notatek prasowych z obu plików .json """
from datetime import datetime  # import niezbędnej metody z modułu 'datetime'
from program_files.JsonOperations import *  # import metod, operujących na plikach .json (metody własne)


class PressNotesDeleter:
    """ Klasa 'PressNotesDeleter', odpowiadająca za usuwanie starych notatek prasowych (proces nieodwracalny) """
    def __init__(self, max_year, max_month, max_day):
        """ Tworzenie instancji obiektu klasy 'PressNotesDeleter'; argumentami instancji są rok, miesiąc i dzień, tj.
        data, do której będą usuwane artykuły (wcześniejsze, niż ta data) """
        # uzupełnianie wartości dla miesiąca i dnia, jeśli użytkownik podał pojedyncze cyfry
        if len(str(max_month)) == 1:
            max_month = "0" + str(max_month)
        if len(str(max_day)) == 1:
            max_day = "0" + str(max_day)
        # utworzenie łańcuchowego formatu daty
        max_date_string = str(max_year) + "/" + str(max_month) + "/" + str(max_day)
        # zastosowanie metody 'datetime' w celu przekształcenia daty na domyślny format datetime
        # (rok-miesiąc-dzień godzina-minuty-sekundy); jeśli argumenty nie tworzą odpowiedniego formatu daty zgodnego z
        # wybraną maską (%Y/%m/%d), program wyrzuca wyjątek, obsługiwany w głównym menu
        self.max_date = datetime.strptime(max_date_string, '%Y/%m/%d')
        # pobranie zawartości obu plików .json
        self.press_notes = get_data_from_json("..//json_files//press_notes.json")
        self.notes_classified = get_data_from_json("..//json_files//notes_classified.json")

    def save_modified_press_notes(self):
        """ Metoda zapisująca zmodyfikowane notatki prasowe do odpowiednich plików .json """
        set_data_to_json("..//json_files//press_notes.json", self.press_notes)
        set_data_to_json("..//json_files//notes_classified.json", self.notes_classified)

    def delete_old_press_notes(self):
        """ Metoda usuwająca stare notatki prasowe z obu plików .json """
        def delete_notes_from_file(notes_data):
            """ Metoda wewnętrzna, usuwająca notatki prasowe z konkretnego pliku """
            deleted_num = 0  # licznik usuniętych notatek
            # iteracja po 'kluczach głównych', tj. portalach dla 'press_notes.json' lub kategoriach dla 'notes_classified.json'
            for main_key in notes_data:
                # wyodrębnienie kluczy notatek prasowych (ich tytułów) i odwrócenie ich kolejności;
                press_notes = notes_data[main_key]
                pn_titles = list(press_notes.keys())
                pn_titles.reverse()
                # pętla, iterująca po tytułach notatek prasowych w kolejności od najstarszej do najnowszej
                for title in pn_titles:
                    current_pn = press_notes[title]
                    # weryfikacja daty notatki prasowej
                    datetime_obj = datetime.strptime(current_pn["Data"], '%Y-%m-%d %H:%M')
                    # jeśli jest ona 'wcześniejsza' niż ustalona data 'maksymalna', notatka jest usuwana
                    if datetime_obj < self.max_date:
                        press_notes.pop(title)
                        deleted_num += 1  # zwiększenie wartości licznika
                    else:
                        # w przeciwnym wypadku, pętla jest przerywana, a proces - zakończony
                        break
            # zwrócenie licznika usuniętych notatek
            return deleted_num

        # część właściwa metody; zastosowanie metody wewnętrznej do usunięcia notatek z obu plików .json
        num_of_deleted = delete_notes_from_file(self.press_notes)
        delete_notes_from_file(self.notes_classified)
        # ile usunięto?
        print(f"Usunięto: {num_of_deleted}")
