# Jan Proniewicz, 297989, Informatyka - Data Science
""" Plik główny; menu obsługi konsolowej aplikacji """
# importowanie wszystkich niezbędnych narzędzi z elementów składowych systemu
from program_files.PressNotesDownloader import *
from program_files.PressNotesDeleter import *
from program_files.PressNotesClassifier import *
from program_files.PressNotesVisualizer import *


def main_menu():
    """ Menu główne aplikacji; to za jego pośrednictwem użytkownik ma dostęp do funkcji systemu; znaki '=' pełnią tylko
     rolę 'estetyczną'/'separacyjną' (wizualnie oddzielają okna menu od siebie) """
    print("===========================================================================================================")
    print("System klasyfikacyjny internetowych notatek prasowych:")
    # "włączenie" systemu, działającego na zasadzie pętli
    all_systems_online = True
    while all_systems_online:
        # menu wychwytuje potencjalne błędy, tj. niepoprawne wartości wpisane przez użytkownika i wraca na początek pętli
        try:
            print("===================================================================================================")
            # główne okno; wybór jednej z wypisanych opcji poprzez podanie w konsoli odpowiedniej cyfry
            option = input("Wybierz opcję:\n1 - Pobierz więcej notatek z internetu (strony: wyborcza.pl, onet.pl, wp.pl);\n"
                           "2 - Usuń 'stare' notatki prasowe;\n3 - Przeprowadź klasyfikację notatek prasowych;\n"
                           "4 - Pokaż notatki prasowe wg kategorii;\n5 - Wyjdź\n")
            # uruchamianie odpowiedniej funkcji systemu na podstawie wybranej opcji w menu; po zakończeniu wykonywania
            # wybranej z funkcji, program wraca na początek pętli (jeżeli użytkownik nie wybrał opcji '5')
            # pobranie nowych notatek prasowych
            if option == '1':
                print("===============================================================================================")
                # podanie roku, miesiąca i dnia, reprezentujących 'granicę' pobierania notatek
                # (program nie będzie pobierał notatek wcześniejszych, niż sprecyzowana data)
                print("Podaj 'najwcześniejszy' dzień (pełna data), do którego notatki będą pobierane:")
                year = input("Rok: ")
                month = input("Miesiąc: ")
                day = input("Dzień: ")
                # utworzenie instancji obiektu 'PressNotesDownloader', odpowiedzialnej za pobieranie nowych notatek/
                # /artykułów z internetu (pobranie i zapis do pliku 'press_notes.json')
                pn_download = PressNotesDownloader(year, month, day)
                pn_download.get_more_press_notes()
                pn_download.save_press_notes()
                print("Pobieranie zakończone pomyślnie!\n")
            # usuwanie starych notatek prasowych / artykułów
            elif option == '2':
                print("===============================================================================================")
                # podanie roku, miesiąca i dnia, reprezentujących 'granicę' usuwania notatek
                # (program zakończy pracę metody, jeżeli dotrze do notatek późniejszych, niż sprecyzowana data)
                print("Podaj 'najpóźniejszy' dzień (pełna data), do którego notatki będą usuwane:")
                print("UWAGA! Proces nieodwracalny!")
                year = input("Rok: ")
                month = input("Miesiąc: ")
                day = input("Dzień: ")
                # utworzenie instancji obiektu 'PressNotesDeleter', odpowiedzialnej za usuwanie starych notatek/
                # /artykułów z obu plików .json (tj. dla pobranych i sklasyfikowanych notatek)
                pn_delete = PressNotesDeleter(year, month, day)
                pn_delete.delete_old_press_notes()
                pn_delete.save_modified_press_notes()
                print("Usuwanie 'starych' notatek prasowych zakończone pomyślnie!\n")
            # klasyfikacja notatek prasowych dostępnych w bazie, tj. pliku 'press_notes.json'
            elif option == '3':
                print("===============================================================================================")
                # użytkownik podejmuje decyzję, czy chce zresetować zawartość pliku 'notes_classified.json' i sklasyfikować
                # wszystkkie notatki od nowa, czy tylko nowo pobrane (musi wprowadzić jedną z dwóch odpowiednich liter)
                print("Czy chcesz skategoryzować notatki od nowa?")
                decision = input("Tak (y) / Nie (n)")
                if decision in ['y', 'n']:
                    # utworzenie instancji obiektu 'PressNotesClassifier', odpowiedzialnej za klasyfikację artykułów
                    pn_classify = PressNotesClassifier()
                    if decision == 'y':
                        # reset pliku 'notes_classified.json' z zaklasyfikowanymi notatkami
                        pn_classify.restart_classification()
                    # przeprowadzenie klasyfikacji i zapis wyników do pliku 'notes_classified.json'
                    pn_classify.classify_press_notes()
                    pn_classify.save_classification_changes()
                    print("Kategoryzacja notatek prasowych zakończona pomyślnie!\n")
                # jeśli 'input' jest nieprawidłowy, system wyrzuci wyjątek, który następnie zostanie obsłużony;
                # program wraca na początek pętli; analogiczna sytuacja występuje w pozostałych funkcjach, z tą różnicą,
                # że pojawienie się błędu wynika z właściwości zastosowanych metod
                else:
                    raise ValueError
            #
            elif option == '4':
                print("===============================================================================================")
                pn_vizualize = PressNotesVisualizer()
                pn_vizualize.continuous_visualization()
            # wyjście z aplikacji, tj. przerwanie pętli
            elif option == '5':
                all_systems_online = False
            # jeśli 'input' opcji jest nieprawidłowy, system wyrzuci wyjątek, który następnie zostanie obsłużony
            else:
                raise ValueError
        # obsługa wyjątków, tj. wyświetlenie komunikatu o błędzie i powrót na początek pętli
        except (ValueError, IndexError):
            print("Błąd wprowadzonych danych!\n")


if __name__ == "__main__":
    """ Testowanie działania programu, pobierającego i kategoryzującego notatki prasowe """
    main_menu()
