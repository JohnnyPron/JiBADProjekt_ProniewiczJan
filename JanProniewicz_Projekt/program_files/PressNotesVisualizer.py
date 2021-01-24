# Jan Proniewicz, 297989, Informatyka - Data Science
""" Funkcja systemu, odpowiadająca za 'wizualizację' (po prostu - wypisywanie) artykułów z konkretnych kategorii """
from program_files.JsonOperations import *  # import metod, operujących na plikach .json (metody własne)


class PressNotesVisualizer:
    """ Klasa 'PressNotesVisualizer', odpowiadająca za 'prezentację' sklasyfikowanych notatek prasowych """
    def __init__(self):
        """ Utworzenie instancji obiektu klasy """
        # pobranie zawartości pliku 'notes_classified.json'
        self.notes_classified = get_data_from_json("..//json_files//notes_classified.json")
        # sprecyzowanie listy kategorii
        self.categories_list = list(self.notes_classified.keys())

    def show_press_notes_from_category(self, cat_index):
        """ Metoda wypisująca notatki prasowe z jednej kategorii; cat_index - indeks kategorii w stosunku do ustalonej
        listy kategorii """
        # pobranie zbioru notatek dla wybranej kategorii
        category = self.categories_list[int(cat_index)]
        notes_from_cat = self.notes_classified[category]
        # jeśli zbiór nie jest pusty...
        if len(notes_from_cat) != 0:
            # wyodrębnienie kluczy słownika (tj. tytułów artykułów) i odwrócenie ich kolejności;
            # będą one wypisywane w kolejności od najstarszej do najnowszej, ponieważ na konsoli
            # wygodniej będzie czytać artykuły od dołu do góry
            pn_titles = list(notes_from_cat.keys())
            pn_titles.reverse()
            # iteracja po kolejnych tytułach/notatkach i wypisanie wszystkich informacji w ustalonym formacie
            for title in pn_titles:
                note = notes_from_cat[title]
                print(f"Tytuł: \"{note['Tytuł']}\"")
                print(note["Opis"])
                print(f"Data: {note['Data']}")
                print(f"Link do artykułu: {note['URL']}")
                print()
            # napisanie, ile notatek znajduje się łącznie w danej kategorii
            print("Razem: " + str(len(notes_from_cat)))
        # wyświetlenie odpowiedniego komunikatu, jeżeli zbiór notatek z danej kategorii jest pusty
        else:
            print("Kategoria pusta!")

    def continuous_visualization(self):
        """ Metoda otwierająca osobne menu dla 'wyświetlacza' notatek prasowych """
        # 'włączenie' menu, działającego na zasadzie pętli
        visualizing_enabled = True
        while visualizing_enabled:
            print("Notatki z której kategorii chciałbyś zobaczyć?")
            # wybór kategorii (podanie jednej cyfry z poniższych lub 'q'), z której notatki mają być wypisane;
            # jeśli użytkownik poda indeks wychodzący poza zakres listy kategorii lub wprowadzi dane innego typu,
            # program wraca do menu głównego na drodze obsługi wyjątku (w głównym menu)
            cat_index = input("0 - polityka;\n1 - sport;\n2 - piłka nożna;\n3 - zimowy sport;\n4 - tenis;\n5 - sport "
                              "motorowy;\n6 - kolarstwo;\n7 - medycyna;\n8 - koronawirus;\n9 - kultura;\n10 - nauka i "
                              "technika;\n11 - gospodarka;\n12 - kryminalne i wypadki;\n13 - religia i Kościół;\n"
                              "14 - inne.\nNaciśnij 'q' aby wyjść.\n")
            # przerwanie pętli, jeśli użytkownik zdecydował się wyjść
            if cat_index == 'q':
                visualizing_enabled = False
            # zastosowanie metody, wypisującej wszystkie notatki dla wybranej kategorii (dokładniej mówiąc: jej indeksu)
            else:
                self.show_press_notes_from_category(cat_index)
            print()
