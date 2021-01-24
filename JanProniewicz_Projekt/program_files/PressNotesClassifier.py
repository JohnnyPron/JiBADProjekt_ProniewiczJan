# Jan Proniewicz, 297989, Informatyka - Data Science
""" Funkcja systemu, odpowiedzialna za klasyfikację notatek prasowych, znajdujących się w pliku 'press_notes.json' """
from collections import OrderedDict  # import 'uporządkowanego słownika'
from datetime import datetime  # import niezbędnej metody z modułu 'datetime'
import re  # biblioteka 'regex', która przyda się podczas klasyfikacji wg liczby wystąpień słów kluczowych
from program_files.JsonOperations import *  # import metod, operujących na plikach .json (metody własne)


class PressNotesClassifier:
    """ Klasa 'PressNotesClassifier', odpowiadająca za klasyfikację notatek prasowych """
    def __init__(self):
        """ Tworzenie instancji obiektu klasy 'PressNotesClassifier' """
        # pobranie zawartości obu plików .json
        self.notes_to_classify = get_data_from_json("..//json_files//press_notes.json")
        self.notes_classified = get_data_from_json("..//json_files//notes_classified.json")
        # sprecyzowanie słów kluczowych (niezmiennych fragmentów form) dla każdej z kategorii, oprócz 'inne';
        # w nawiasach kwadratowych znajdują się litery 'zamienne', np. 'szczepi[ćł]' oznacza 'szczepić' lub 'szczepił'
        # (technika kompatybilna z 'regex')
        politics_key_words = ["Dud[aęy]", "Trump", "Biden", "Kaczyńsk", "Clinton", "Morawieck", "Ziobr", "Korwin", "Obam",
                              "Putin", "Łukaszenk", "Hołowni", "Trzaskowk", "minister", "ministr", "PiS", "PO", "Sprawiedliwoś",
                              "Platform", "Konfederacj", "PSL", "trybunał", "sejm", "senat", "prezyden[ct]", "ustaw[aęiy]",
                              "opozycj", "polity[ck]", " rząd", "Rząd", "Kim Dzong", "poseł", "posł[aeoó]", "konstytucj",
                              "parlament", "referendum", "Tusk", "Uni[aąęi] Europejsk", "UE", "parti", "starost", "ojczyzn",
                              "nar[oó]d", "Rad[ayz]", "premier", "Gowin", "prawic", "lewic", "koalicj", "demokrac", "Kapitol",
                              "autorytar", "totalitar", "wojn[aąęiy]", "wojenn", "komisj", "przywódc", "protest", "Paszynian",
                              "Alijew", "wybor[aoóy]", "wyborcz", "ONZ", "NATO", "Kongres", "Kosiniak", "ambasador", "Macierewicz",
                              "smoleńsk", "spisek", "spisk", "generał", "sekretarz", "demonstracj", "Nawaln", "zwolenni[ck]"]
        football_key_words = ["piłkarz", " bramk", "Bramk", "Lewandowsk", "Messi", "Cristiano Ronaldo", "mundial", "nożn[aąe]"]
        wintersport_key_words = ["narty", "nartach", "narciarski", "Stoch", "Kuback", "Ży[lł][aąęy]", "Stęka[lł]",
                                 "skoczni", "łyżwiar", "łyżw[ay]", "hokej", "curling", "lodowisk"]
        tenis_key_words = [" tenis", "Tenis", "Radwańsk", "Hurkacz", "Australian Open"]
        moto_key_words = ["Formuł", "F1", " bolid", "Bolid" "Kubic", "Ferrari", "Schumacher", "rajdow[iy]"]
        cycling_key_words = [" rower", "Rower", " kolarz", "Kolarz", "Tour de", "peleton", "kolarsk"]
        sports_key_words = ["sport", "zawod[aóy]", "mistrz", "zawodnik", "drużyn", "turniej", "medal", "kibic", "doping",
                            "igrzysk", "olimpiad", "olimpijsk", "trener"]
        coronavirus_key_words = ["koronawirus", "pandemi", "COVID-19", "SARS-CoV-2", "obostrze", "kwarantann", "lockdown",
                                 "szczepi[eo][nń]", "szczepi[ćł]", "restrykcj[ei] rząd", "restrykcjach rząd",
                                 "restrykcjom rząd", "epidemi", "sanitarn", "covid"]
        health_key_words = ["szpital", "medyc", "WHO", "NFZ" "Zdrowia", "lekarstw", "chirurg", "przeszczep", "lekarz",
                            "okulist", "przychodni", "chor[oó]b", "medyk", "pogotowi", "ratowni[ck]", "pacjent",
                            "nowotw[oó]r", "pielęgniar", "diagnoz", "TOPR", "szkod[lz]"] + coronavirus_key_words
        culture_key_words = ["film", "utw[oó]r", "piosenk", "książk", "autor", "serial", "zabytk", "zabytek", "teatr",
                             "kin[ao]", "kinie", "muzyk", "muzyczn", "koncert", "koncercie", "sztuk", "twórc",
                             "arty[sś][ct]", "Mickiewicz", "romanty[cz]", "renesans", "literatur", "literack", "ballad",
                             "kultur", "muzeum", "histori", " śpiew", "Śpiew", "przeb[oó]j"]
        sciandtech_key_words = ["kosmos", "NASA", "kosmiczn", "galakty", "odkryci", "odkrywać", "naukow[ci]", "archeolo",
                                "paleontolo", "geolog", "wynalaz", "wynaleź", "YouTube", "Spotify", "Twitter", "Facebook",
                                "CD Project", "komputer", "epok[ai]", "epokow", "histori", "patent", "DNA", "specjalist",
                                "bada[jłn]", "innowac", "uniwersyte", "uczelni", "akademi", "przełom", "nauk[ai]", "technologi",
                                "rozw[oó]j", "zdoby[ct]", "serwis", "użytkowni", "portal", "anali[zt]", "medi[aó]"]
        economy_key_words = ["przedsiębiorstw", "przedsiębiorc[aóy]", "inflacj", "doch[oó]d", "podatk", "bank", "restaura[ct]",
                             "biznes", "koszt", "splajtow", "usług", "finans", "strat", "gospodar", "turyst", "turyści",
                             "tys. zł", "mln zł", "mld zł", "tysiąc zł", "tysiące zł", "tysięcy zł" "milion zł", "miliony zł",
                             "milionów zł", "miliard zł", "miliardy zł", "miliardów zł", "dolarów", "funtów", "euro",
                             "pieni[ąę]dz", "Skarb", "bitcoin", "500 plus", "wypłac[ao]n", "podwyżk", "obniżk", "obniżek",
                             "podwyżek" "budże[ct]", "knajp", "branż", "wynagrodze[nń]", " cię[cć]", "Cię[cć]", "opłat",
                             "przetarg"]
        criminal_key_words = ["zaginion", "zagin[ąę]ł", "mordowan", "morderstw", "morderc", "zabójstw", "zabójc", "kradzież",
                              "kradzion", "porwan", "narkotyk", "przemyt", "przemycenie", "przmycon", "terroryst", "policj",
                              "milicj", "mandat", "wypadek", "wypadk", "straż", "strajk", "zamieszki", "zamieszkach",
                              "zamieszek", "Kapitol", "plądrowa", "zaatakowa", "podejrzan", "sprawc[aoóy]", "skazan", "wyrok",
                              "więzi[eo]n", "pozbawieni[ae] wolności", "dożywoci[ae]", "legaln", "promil", "nietrzeźw",
                              "zwłok", "śledztw", "przestępstw", "prokurat[ou]r", "sąd", "imitacj", "podróbk", "podr[ao]bion",
                              "pożar", "spłon[ąę]ł", "uratowa", "zatru[cćł]", "otru[cćł]", "alarmow", "pod wpływem alkoholu",
                              "potrąci", "potrącon", "zatrzyma[ćn]", "poszukiwan", "tragedi", "tragiczn", "nie ży[jł]",
                              "śmier[cć]", "śmierteln", "życi", "żyć", "przestępcz", "fałszerstw", "fałszowan", "wyłudz[ae]nie",
                              "nieprzytomn", "rann[aiy]", "zderzy", "zderz[eo]n", "złodzie[ij]", "zarzut", "zabił", "zabici",
                              "przeży[ćł]", "strzel[ai]", "n[oó]ż", "pomoc", "zbrodni", "ciał[ao]", "zgin[ąę][lł]", "rozbi[łt]",
                              "martw[aiy]", "apelacj", "FBI", "uzbroj[eo]n", "sprawiedliwoś", "śledcz", "aresz[ct]", "CIA",
                              "samobój[cs]", "katastrof", "wyciek", "ewaku[ao]", "pijan", "sędzi", "włam[ay][lłnw]",
                              "napastni[ck]", "uderzy[ćł]", "zmarł", "gwał[ct]", "molestowan", "nieletn"]
        religion_key_words = ["kości[eoó][lł]", "duchown", "chrześcija", "ksiądz", "księża", "księży", "kapłan", "biskup",
                              "zakon", "papież", "papieski", "islam", "muzułman", "prawosław[in]", "katolic", "katolizm",
                              "żydowsk", "Żyd", "chrzest", "chrzczon", "bierzmowan", "święt[ay]", "Boże", "Wigili", "świątecz",
                              "najświętsz", "kolęd", "Wielkanoc", "Jezus", "Chrystus", "B[oó]g", "msz[ay]", "modli[ćłt]",
                              "kaplic", "diecezj", "katedr", "misjonar", "wiern[aiy]", "religi", "wierze[nń]", "dominikan",
                              "franciszkan", "benedyktyn", "Mary[ij]", "ojc[aeiu]", "proboszcz", "parafi"]
        # umieszczenie zbiorów słów kluczowych do jednej listy
        key_words_list = [politics_key_words, football_key_words, wintersport_key_words, tenis_key_words, moto_key_words,
                          cycling_key_words, sports_key_words, health_key_words, coronavirus_key_words, culture_key_words,
                          sciandtech_key_words, economy_key_words, criminal_key_words, religion_key_words]
        # wylistowanie możliwych kategorii, poza 'inne'
        self.categories_list = ["polityka", "piłka nożna", "zimowy sport", "tenis", "sport motorowy", "kolarstwo",
                                "sport", "medycyna", "koronawirus", "kultura", "nauka i technika", "gospodarka",
                                "kryminalne i wypadki", "religia i Kościół"]
        # uporządkowanie słów kluczowych w słowniku: klucz=kategoria, wartość=słowa_kluczowe
        self.key_words_for_categories = {}
        for i in range(len(self.categories_list)):
            self.key_words_for_categories[self.categories_list[i]] = key_words_list[i]

    def save_classification_changes(self):
        """ Zapisanie zaklasyfikowanych notatek do pliku notes_classified.json """
        set_data_to_json("..//json_files//notes_classified.json", self.notes_classified)

    def restart_classification(self):
        """ Reset, tj. opróżnianie zbioru sklasyfikowanych notatek prasowych, żeby było można je podzielić od nowa """
        for category in self.notes_classified:
            self.notes_classified[category] = {}

    def check_if_already_classified(self, title):
        """ Metoda dprawdzająca, czy dana notatka (title) jest już gdzieś zaklasyfikowana """
        # iteracja po poszczególnych kategoriach w pliku notes_classified.json
        for category in self.notes_classified:
            notes_from_cat = self.notes_classified[category]
            if title in notes_from_cat:
                return True
        return False

    def how_many_notes_in_categories(self):
        """ Zliczanie notatek prasowych w każdej z kategorii """
        print("Liczba artykułów/notatek w każdej z kategorii:")
        for category in self.notes_classified:
            print(f"{category.capitalize()}: {len(self.notes_classified[category])}")

    def sort_notes_by_date(self):
        """ Sortowanie notatek prasowych w poszczególnych kategoriach od najnowszej do najstarszej """
        # iteracja po kategoriach
        for cat in self.notes_classified:
            notes_to_sort = self.notes_classified[cat]
            # jeśli zbiór dla danej kategorii jest pusty, dalsze kroki są pomijane
            if len(notes_to_sort) != 0:
                # zastosowanie zaimportowanej metody 'datetime', w celu zmiany formatu daty ze 'string' na datetime
                # w każdej z notatek prasowych
                for note in notes_to_sort:
                    art_date_datetime = datetime.strptime(notes_to_sort[note]["Data"], '%Y-%m-%d %H:%M')
                    notes_to_sort[note]["Data"] = art_date_datetime
                # wykorzystanie 'uporządkowanego słownika', w celu posortowania (malejąco) notatek prasowych wg daty publikacji
                notes_ordered = OrderedDict(sorted(notes_to_sort.items(), key=lambda x: x[1]["Data"], reverse=True))
                # zmiana formatu daty z powrotem na 'string' (json nie ma formatu zamiennego dla datetime)
                for note in notes_ordered:
                    # ostatnie trzy znaki w 'datetime' reprezentują sekundy, które są niepotrzebne
                    notes_ordered[note]["Data"] = str(notes_ordered[note]["Data"])[:-3]
                # wprowadzenie uporządkowanego zbioru do całego zbioru sklasyfikowanych notatek
                self.notes_classified[cat] = notes_ordered

    def classify_press_notes(self):
        """ Metoda klasyfikująca notatki prasowe na dwa sposoby. """
        def classify_by_label(note_to_classify):
            """ Metoda wewnętrzna klasyfikująca notatki prasowe wg zakładek, z których pochodzą; note_to_classify -
            - aktualna notatka """
            label = note_to_classify["Zakladka"]  # wyodrębnienie zakładki notatki prasowej
            # zbadanie zakładki i specyfikacja kategorii, która by jej odpowiadała
            if label == "polityka":
                category = self.categories_list[0]
            elif label in ["sport", "pilka-nozna", "skoki-narciarskie", "zimowe", "formula-1", "moto", "tenis",
                           "kolarstwo"]:
                category = self.categories_list[6]
                # notatki z zakładek, odpowiadającym konkretnym dyscyplinom, będą należeć zarówno do kategorii sport,
                # jak i kategorii dla ich deyscypliny
                category2 = ""
                if label == "pilka-nozna":
                    category2 = self.categories_list[1]
                elif label in ["skoki-narciarskie", "zimowe"]:
                    category2 = self.categories_list[2]
                elif label in ["formula-1", "moto"]:
                    category2 = self.categories_list[4]
                elif label == "tenis":
                    category2 = self.categories_list[3]
                elif label == "kolarstwo":
                    category2 = self.categories_list[5]
                if category2 != "":
                    categories_for_note.append(category2)
            elif label in ["zdrowie", "koronawirus"]:
                category = self.categories_list[7]
                # z reguły, notatki z zakłądki 'koronawirus' są mocno powiązane z 'medycyną'
                if label == "koronawirus":
                    categories_for_note.append(self.categories_list[8])
            elif label == "kultura":
                category = self.categories_list[9]
            elif label in ["nauka", "technika"]:
                category = self.categories_list[10]
            elif label == "gospodarka":
                category = self.categories_list[11]
            elif label == "religia":
                category = self.categories_list[13]
            # jeśli zakładka nie odpowiada żadnej kategorii, dalsze operacje są pomijane
            else:
                category = None
            if category is not None:
                # umieszczenie zidentyfikowanej kategorii na liście potencjalnych kategorii dla notatki
                # (zaimplementowana w metodzie nadrzędnej)
                categories_for_note.append(category)

        def classify_by_key_words(note_to_classify):
            """ Metoda wewnętrzna klasyfikująca notatki prasowe na podstawie wystąpień określonych słów kluczowych;
             note_to_classify - aktualna notatka"""
            # klasyfikacja bazuje na liczbie wystąpień określonych wyrażeń kluczowych w tytule i lead'ie (opisie)
            note_title = note_to_classify["Tytuł"]
            note_lead = note_to_classify["Opis"]
            text_to_check = note_title + " " + note_lead

            def classify_by_single_occurence(current_category, keyword):
                """ Kolejna metoda wewnętrzna, która klasyfikuje notatkę na podstawie pojedynczego wystąpienia
                słowa kluczowego (keyword); current_category - aktualnie badana kategoria """
                # metoda 'search' biblioteki 're(gex)' wychwytuje pierwsze wystąpienie wyrażenia w 'stringu'
                if re.search(keyword, text_to_check) is not None:
                    # jeśli wyrażenie zostanie znalezione, kategoria jest dodawana do listy potencjalnych
                    categories_for_note.append(current_category)
                    # dodatkowo, jeśli notatka należała do jednej z dyscyplin sportu, to zostaje jej również
                    # przydzielona kategoria 'sport' (trgo samego nie robi dla 'koronawirusa' i 'medycyny', gdyż
                    # nie każde wydarzenie związane z koronawirusem jednoznacznie wiąże się z medycyną)
                    if current_category in ["piłka nożna", "zimowy sport", "tenis", "sport motorowy", "kolarstwo"]:
                        categories_for_note.append("sport")
                    # zwracane wartości wpływają na dalsze prcesy w metodzie nadrzędnej
                    return True
                else:
                    return False

            # iteracja po kolejnych kategoriach
            for category in self.key_words_for_categories:
                # dlasze procedury są pomijane, jeżeli kategoria już się znajduje na liście
                if category not in categories_for_note:
                    key_words = self.key_words_for_categories[category]  # pobranie słów klucz
                    num_of_occurrences = 0  # licznik wystąpień słów kluczowych w tytule i opisie notatki
                    # iteracja po kolejnych słowach kluczowych
                    for k_word in key_words:
                        # jeśli kategoria reprezentuje jedną z określonych dyscyplin sportu lub koronawirusa,
                        # dokonuje się klasyfikacji na podstawie pojedynczego wystąpienia (ponieważ są to tematyki o
                        # bardziej zawężonym zakresie; wciąż wiążą się z tym błędy klasyfikacji)
                        if category in ["piłka nożna", "zimowy sport", "tenis", "sport motorowy", "kolarstwo",
                                        "koronawirus"]:
                            # jeśli się uda zaklasyfikować notatkę, pętla jest przerywana i przechodzi do kolejnej kategorii
                            if classify_by_single_occurence(category, k_word):
                                break
                            # w przeciwnym wypadku, ponawia proces dla tego samego słowa, zaczynającego się od dużej litery
                            else:
                                if k_word.islower():
                                    k_word_capitalized = k_word.capitalize()
                                    if classify_by_single_occurence(category, k_word_capitalized):
                                        break
                        # standardowo, klasyfikacja odbywa się poprzez zliczanie wystąpień wyrażeń kluczowych
                        else:
                            # metoda 'findall' biblioteki 're(gex)' generuje listę wystąpień badanego wyrażenia w 'stringu'
                            occurrences_list = re.findall(k_word, text_to_check)
                            # zwiększenie licznika wystąpień o długość listy wystąpień
                            num_of_occurrences += len(occurrences_list)
                            # powtórzenie tej samej procedury dla tego samego wyrażenia, zaczynającego się od dużej litery
                            if k_word.islower():
                                k_word_capitalized = k_word.capitalize()
                                occurrences_list = re.findall(k_word_capitalized, text_to_check)
                                num_of_occurrences += len(occurrences_list)
                            # jeśli liczba wystąpień słów kluczowych będzie większa lub równa 3, kategoria zostaje dodana
                            # do listy potencjalnych kategorii; pętla zostaje przerwana i przechodzi do następnej kategorii
                            if num_of_occurrences >= 3:
                                categories_for_note.append(category)
                                break

        # właściwa część metody 'classify_press_notes'
        # iteracja po kolejnych zbiorach notatek z konkretnych portali
        for notes_source in self.notes_to_classify:
            press_notes = self.notes_to_classify[notes_source]
            # iteracja po kolejnych notatkach (tytułach)
            for title in press_notes:
                # weryfikacja, czy dana notatka już została gdzieś zaklasyfikowana
                if self.check_if_already_classified(title):
                    # jeśli tak, pętla zostaje przerwana (można przypuszczać, że następne notatki też są zaklasyfikowane)
                    break
                # przygotowanie listy potencjalnych kategorii dla notatki prasowej
                categories_for_note = []
                # wyszukiwanie potencjalnych kategorii dla aktualnej notatki prasowej
                # (najpierw wg zakładki, potem - po słowach kluczowych)
                the_note = press_notes[title]
                classify_by_label(the_note)
                classify_by_key_words(the_note)
                # zapisanie notatki prasowej w zbiorach, odpowiadajacych zebranym kategoriom
                for cat in categories_for_note:
                    notes_from_cat = self.notes_classified[cat]
                    notes_from_cat[title] = the_note
                # jeśli dla notatki nie znaleziono żadnej kategorii, zostaje ona przydzielona do zbiotu 'inne'
                if len(categories_for_note) == 0:
                    self.notes_classified["inne"][title] = the_note
        # posortowanie notatek w każdej kategorii w kolejności od najnowszej do najstarszej
        self.sort_notes_by_date()
        # wypisanie, ile notatek znajduje się w każdej z kategorii
        self.how_many_notes_in_categories()
