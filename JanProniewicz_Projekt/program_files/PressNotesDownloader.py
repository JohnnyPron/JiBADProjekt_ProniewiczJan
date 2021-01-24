# Jan Proniewicz, 297989, Informatyka - Data Science
""" Funkcja systemu, koncentrująca się na pobieraniu nowych notatek prasowych / artykułów z internetu;
 Wybrane platformy: wyborcza.pl, wiadomości.onet.pl, sport.onet.pl, wiadomości.wp.pl, sportowefakty.wp.pl """
import requests  # biblioteka, która posłuży do pobrania zawartości stron internetowych z podanego URL
from bs4 import BeautifulSoup  # metoda, która przetworzy pobraną zawartość na czytelny kod html i wydzieli jego odpowiednie części
from collections import OrderedDict  # import 'uporządkowanego słownika'
from datetime import datetime  # import niezbędnej metody z modułu 'datetime'
from program_files.JsonOperations import *  # import metod, operujących na plikach .json (metody własne)


class PressNotesDownloader:
    """ Klasa 'PressNotesDownloader', która będzie pobierała notatki prasowe z internetu, tj. ze strony 'Wyborczej',
    'Onetu' i 'Wirtualnej Polski' (wp)"""
    def __init__(self, min_year, min_month, min_day):
        """ Tworzenie instancji obiektu klasy 'PressNotesDownloader'; argumentami instancji są rok, miesiąc i dzień, tj.
         data, do której będą pobierane artykuły (późniejsze, niż ta data) """
        # uzupełnianie wartości dla miesiąca i dnia, jeśli użytkownik podał pojedyncze cyfry
        if len(str(min_month)) == 1:
            min_month = "0" + str(min_month)
        if len(str(min_day)) == 1:
            min_day = "0" + str(min_day)
        # utworzenie łańcuchowego formatu daty
        min_date_string = str(min_year) + "/" + str(min_month) + "/" + str(min_day)
        # zastosowanie metody 'datetime' w celu przekształcenia daty na domyślny format datetime
        # (rok-miesiąc-dzień godzina-minuty-sekundy); jeśli argumenty nie tworzą odpowiedniego formatu daty zgodnego z
        # wybraną maską (%Y/%m/%d), program wyrzuca wyjątek, obsługiwany w głównym menu
        self.min_date = datetime.strptime(min_date_string, '%Y/%m/%d')
        # pobranie zawartości pliku 'press_notes.json', gdzie będą umieszczane artykuły po pobraniu
        self.press_notes = get_data_from_json("..//json_files//press_notes.json")
        # zakładki 'wyborcza.pl', z których będą pobierane artykuły
        wyborcza_labels = ["swiat", "kraj", "sport", "zdrowie", "gospodarka", "technika", "nauka", "kultura"]
        # lista ciągów cyfr, charakterystycznych dla URL poszczegółnych zakładek
        # (w tej samej kolejności co odpowiadające im zakładki)
        html_id_for_wyborcza = ["0,75399", "0,75398", "0,154903", "TylkoZdrowie/0,0", "0,155287", "0,156282", "0,75400",
                                "0,75410"]
        # uporządkowanie tych fragmentów URL dla zakładek Wyborczej w słowniku
        self.wyborcza_categories = {}
        for i in range(0, len(wyborcza_labels)):
            self.wyborcza_categories[wyborcza_labels[i]] = html_id_for_wyborcza[i]
        # zakładki 'wiadomosci.onet.pl' i 'sport.onet.pl', z których będą pobierane artykuły
        self.onet_labels = ["kraj", "swiat", "tylko-w-onecie", "religia", "pilka-nozna", "skoki-narciarskie", "formula-1",
                            "tenis", "kolarstwo", "krakow", "warszawa", "lodz", "wroclaw", "szczecin", "bialystok",
                            "poznan", "rzeszow", "trojmiasto", "slask", "opole"]
        # zakładki 'wiadomosci.wp.pl' i 'sportowefakty.wp.pl', z których będą pobierane artykuły
        self.wp_labels = ["koronawirus", "polska", "swiat", "spoleczenstwo", "polityka", "nauka", "slask", "krakow",
                          "najnowsze", "pilka-nozna", "zimowe", "tenis", "moto", "kolarstwo"]

    def save_press_notes(self):
        """ Metoda zapisująca pobrane notatki prasowe do pliku press_notes.json """
        set_data_to_json("..//json_files//press_notes.json", self.press_notes)

    def get_more_press_notes(self):
        """ Metoda 'główna', pobierająca notatki ze wszystkich trzech platform i wyświetlająca liczbę wszystkich
        aktualnych notatek w 'bazie' """
        self.scrape_wyborcza()
        self.scrape_onet()
        self.scrape_wp()
        self.how_many_notes_in_total()

    def sort_notes_by_date(self, notes_to_sort):
        """ Sortowanie notatek prasowych z konkretnego źródła (notes_to_sort) od najnowszej do najstarszej """
        # sprawdzenie, czy zbiór notatek nie jest przypadkiem pusty
        if len(notes_to_sort) != 0:
            # iteracja po kolejnych artykułach w zbiorze
            for note in notes_to_sort:
                # zmiana formatu daty artykułów ze 'string' na 'datetime';
                # data publikacji musi mieć format: rok-miesiąc-dzień godzina:minuty
                art_date_datetime = datetime.strptime(notes_to_sort[note]["Data"], '%Y-%m-%d %H:%M')
                notes_to_sort[note]["Data"] = art_date_datetime
            # zastosowanie 'OrderedDict', w celu posortowania (malejąco) artykułów wg ich daty publikacji
            notes_ordered = OrderedDict(sorted(notes_to_sort.items(), key=lambda x: x[1]["Data"], reverse=True))
            # zmiana formatu daty notatek z powrotem na 'string' (json nie ma formatu zamiennego dla datetime)
            for note in notes_ordered:
                # ostatnie trzy znaki są ignorowane, gdyż reprezentują one sekundy (:ss), które nie są ważne dla systemu
                notes_ordered[note]["Data"] = str(notes_ordered[note]["Data"])[:-3]
            # zwrócenie posortowanego zbioru
            return notes_ordered
        # jeśli zbiór notatek jest pusty, nie ma co sortować i notes_to_sort jest z powrotem zwracane
        else:
            return notes_to_sort

    def check_if_article_is_too_old(self, datetime_string):
        """ Kontrola daty publikacji artykułów (czy nie jest 'za wczesna') """
        # zmiana formatu daty publikacji
        datetime_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
        # porównanie z ustaloną, 'minimalną' datą; jeśli aktualny artykuł jest 'wcześniejszy', dlasze funkcje podejmą
        # odpowednie kroki
        if datetime_obj < self.min_date:
            return True
        return False

    def _modify_datetime_format(self, datetime_str):
        """ Prywatna metoda, przekształcająca format daty (łańcuch znaków) z 'dzień-miesiąc-rok czas'
        (maska: 00-00-0000 00:00) na 'rok-miesiąc-dzień czas' (maska: 0000-00-00 00:00)"""
        day = datetime_str[0:2]
        month = datetime_str[3:5]
        year = datetime_str[6:10]
        time = datetime_str[11:]
        return year + "-" + month + "-" + day + " " + time

    def _get_soup(self, url):
        """ Pobranie zawartości strony na podstawie url i przekształcenie jej na czytelny kod html """
        r = requests.get(url)  # pobranie
        soup = BeautifulSoup(r.content, features="html.parser")  # przekształcenie na odpowiedni format
        return soup

    def _check_if_title_repeats(self, press_source, title, category):
        """ Weryfikacja 'powtórek' tytułów artykułów; press_source - zbiór notatek do weryfikacji (z konkretnego portalu),
        title - tytuł aktualnego artykułu, category - aktualna zakładka badanego portalu; 'YES' - artykuł się powtarza,
        'MAYBE' - tytuł się powtarza, ale pochodzi z innej zakładki, 'NO' - artykuł jest zupełnie nowy """
        # jeśli jakimś zrządzeniem losu tytuł będzie pusty, dla zachowania bezpieczeństwa, program zwróci MAYBE''
        if title is None:
            return "MAYBE"
        # czy artykuł występuje w aktualnym zbiorze?
        if title in press_source:
            current_art = press_source[title]
            # czy pochodzi z tej samej zakładki?
            if current_art["Zakladka"] == category:
                return "YES"
            return "MAYBE"
        return "NO"

    def how_many_notes_in_total(self):
        """ Wypisanie liczby pobranych notatek prasowych, znajdujących się w bazie """
        print("Liczba notatek prasowych w bazie:")
        total = 0  # przygotowanie licznika wszystkich artykułów
        # wypisywanie liczby notatek z poszczególnych portali
        for source in self.press_notes:
            print(f"{source.capitalize()}: {len(self.press_notes[source])}")
            total += len(self.press_notes[source])  # zwiększenie licznika 'total'
        # ile jest wszystkich artykułów razem?
        print(f"Razem: {total}")

    def scrape_wyborcza(self):
        """ Metoda wykoująca Web Scraping na stronie 'Wyborczej'; w innych słowach - metoda wychwytująca odpowiednie
        informacje o notatkach prasowych z kodu html 'Wyborczej' (tylko pierwsza stronica) """
        # pobranie aktualnego zbioru artykułów z Wyborczej
        wyborcza_news = self.press_notes["wyborcza"]
        # iteracja po kolejnych ustalonych zakładkach Wyborczej
        for cat in self.wyborcza_categories:
            # pobranie zawartości z internetu na podstawie URL
            url = "https://wyborcza.pl/" + self.wyborcza_categories[cat] + ".html"
            soup = self._get_soup(url)
            # wyodrębnienie odpowiedniego 'bloku' strony (blok zawierający spis artykułów na stronie)
            body = soup.find("div", {"class": "body"})
            # wyodrębnienie poszczególnych 'artykułów' (ich 'bloczków') z wcześniejszego bloku
            articles = body.find_all("li", {"class": ["entry even article", "entry odd article"]})
            # iteracja po wyodrębnionych notatkach prasowych
            for note in articles:
                # wyodrębnienie tytułu i linka do artykułu z html 'bloczka'; zakładka 'sport' ma nieco inny format niż
                # pozostałe
                if cat == "sport":
                    title = note.find("h3").text.strip()
                    art_url = note.find("h3").find("a").get("href")
                else:
                    title = note.find("h2").text.strip()
                    art_url = note.find("h2").find("a").get("href")
                # sprawdzenie, czy tytuł się powtarza wśród notatek Wyborzej
                title_repeats = self._check_if_title_repeats(wyborcza_news, title, cat)
                # jeśli tak, pętla jest przerywana i program bada następną zakładkę (gdyż następne artykuły w aktualnej
                # zakładce są już najpewniej 'stare', tj. dawno zapisane w 'bazie')
                if title_repeats == "YES":
                    break
                # jeśli 'może', program przerywa iterację pętli i przechodzi do następnego artykułu
                elif title_repeats == "MAYBE":
                    continue
                # pobranie zawartości z html 'bloczka' na temat lead'a i daty publikacji (format dzień-miesiąc-rok czas)
                lead = note.find("p", {"class": "lead"}).text.strip()
                original_date = note.find("span", {"class": "when"}).text
                # przekształcenie daty publikacji na ustalony format rok-miesiąc-dzień godzina:minuty
                art_date = self._modify_datetime_format(original_date)
                # sprawdzenie, czy artykuł nie jest 'za stary'; jeśli tak, pętla jest przerywana, a program bada
                # następną zakładkę
                if self.check_if_article_is_too_old(art_date):
                    break
                # zapisanie pobranych danych o artykule w słowniku i umieszczenie ich w zbiorze notatek Wyborczej
                pressnote_info = {"Tytuł": title, "Opis": lead, "Data": art_date, "URL": art_url, "Zakladka": cat}
                wyborcza_news[title] = pressnote_info
        # posortowanie pobranych notatek w kolejności od najnowszej do najstarszej
        self.press_notes["wyborcza"] = self.sort_notes_by_date(wyborcza_news)

    def scrape_onet(self):
        """ Metoda wychwytująca informacje o notatkach prasowych z kodu html Onetu """
        onet_news = self.press_notes["onet"]  # pobranie aktualnego zbioru artykułów z Onetu

        def create_press_note(art_url, category):
            """ Metoda wewnętrzna, pobierająca i zapisująca odpowiednie dane o notatce prasowej; art_url - link do
            aktualnego artykułu, category - aktualnie badana zakładka; True - wymuszenie pominięcia iteracji w pętli
            'nadrzędnej' (continue), False - przerwanie pętli 'nadrzędnej' (break) """
            # jeśli artykuł nie pochodzi z jednej z niżej podanych stron iteracja jest pomijana (zabezpieczenie przed
            # linkami dla reklam lub artykułami o nieodpowiednim formacie)
            if "wiadomosci.onet.pl" not in str(art_url) and "sport.onet.pl" not in str(art_url):
                return True
            # pobranie zawartości ze strony artykułu w postaci kodu html
            soup2 = self._get_soup(art_url)
            # pobranie informacji dot. tytułu notatki prasowej
            title = soup2.find("h1", {"class": "mainTitle"}).text.strip()
            # sprawdzenie, czy notatka się powtarza w zbiorze artykułów z Onetu
            title_repeats = self._check_if_title_repeats(onet_news, title, category)
            if title_repeats == "YES":
                return False  # przerwanie pętli i przejście do następnej zakładki
            elif title_repeats == "MAYBE":
                return True  # pominięcie iteracji i przejście do następnego artykułu
            # pobranie informacji o lead'ie i dacie publikacji artykułu
            lead = soup2.find("div", {"id": "lead"}).text.strip()
            art_date = soup2.find("meta", {"itemprop": "datePublished"}).get("content")[:16]  # potrzebne jest tylko 16
            # pierwszych znaków (rok-miesiąc-dzień godzina:minuty (maska: 0000-00-00 00:00))
            # sprawdzenie, czy notatka nie jest 'za stara'; analogicznie do 'scrape_wyborcza'
            if self.check_if_article_is_too_old(art_date):
                return False
            # zapisanie zdobytych danych do słownika i umieszczenie powstałej notatki w zbiorze artykułów Onetu
            pressnote_info = {"Tytuł": title, "Opis": lead, "Data": art_date, "URL": art_url, "Zakladka": category}
            onet_news[title] = pressnote_info
            return True

        def scrape_onet_news_and_sport(category):
            """ Metoda wewnętrzna, wykonująca web scraping na 'głównych' zakładkach 'wiadomosci.onet.pl' (nie dotyczących
            konkretnych miast) oraz 'sport.onet.pl'; artykuły na tych zakładkach są 'wylistowane', podobnie do Wyborczej;
            category - aktualnie badana zakładka """
            # przygotowanie URL dla aktualnej zakładki
            if category in ["kraj", "swiat", "tylko-w-onecie", "religia"]:
                url = "https://wiadomosci.onet.pl/" + category
                if category == "religia":
                    url = url + "/aktualnosci"
            else:
                url = "https://sport.onet.pl/"
                if category == "skoki-narciarskie":
                    url = url + "zimowe/"
                url = url + category
            # pobranie zawartości zakładki w postaci kodu html
            soup = self._get_soup(url)
            # wyselekcjonowanie 'bloku' html, poświęconego artykułom
            stream_section = soup.find("section", {"class": "stream"})
            # wyselekcjonowanie poszczególnych 'bloczków', odpowiadających kolejnym notatkom prasowym
            articles = stream_section.find_all("div", {"class": "listItem listItemSolr itarticle"})
            # iteracja po kolejnych notatkach
            for note in articles:
                # wychwycenie i obsługa wyjątku, jeżeli element, który program próbował wyodrębnić, nie istniał
                # (w związku z nieodpowiednim 'niestandardowym' formatem strony artykułu); pominięcie iteracji
                try:
                    # pobranie linka do oryginalnego artykułu z 'bloczka';
                    # ostatni z możliwych elementów typu 'anchor' w html bloczka
                    art_url = note.find_all("a")[-1].get("href")
                    # dalsze operacje na html samego artykułu (w tym pobranie reszty informacji o notatce) oraz podjęcie
                    # decyzji o postąpieniu z pętlą (patrz.: komentarze w 'create_press_note')
                    should_we_keep_going = create_press_note(art_url, category)
                    if should_we_keep_going:
                        continue
                    else:
                        break
                except AttributeError:
                    continue

        def scrape_onet_regional(city):
            """ Metoda wewnętrzna, wykonująca web scraping na zakładkach 'wiadomosci.onet.pl', dot. wybranych miast;
            artykuły na tych zakładkach są ułożone jak 'kafelki'; city - aktualnie badane miasto/zakładka """
            # przygotowanie url zakładki i pobranie zawartości jej strony
            url = "https://wiadomosci.onet.pl/" + city
            soup = self._get_soup(url)
            # wyodrębnienie 'bloku' z poszukiwanymi artykułami
            items_section = soup.find("div", {"class": "items solrList"})
            # wyodrębnienie poszczególnych 'kafelków' (ich elementów typu 'anchor'), odpowiadających kolejnym artykułom
            article_anchors = items_section.find_all("a", {"class": ["itemBox itemBoxBig itemBoxLast",
                                                                     "itemBox itemBoxNormal",
                                                                     "itemBox itemBoxNormal itemBoxLast"]})
            # iteracja po kolejnych notatkach
            for anchor in article_anchors:
                # obsługa wyjątku na wypadek natrafienia na stronę z innym formatem
                try:
                    # pobranie linka do oryginalnego artykułu i wykorzystanie go do dalszej analizy
                    art_url = anchor.get("href")
                    should_we_keep_going = create_press_note(art_url, city)
                    # podjęcie decyzji o postąpieniu z pętlą (patrz.: komentarze w 'create_press_note')
                    if should_we_keep_going:
                        continue
                    else:
                        break
                except AttributeError:
                    continue

        # właściwa część metody 'scrape_onet'; iteracja po kolejnych ustalonych zakładkach Onetu
        for cat in self.onet_labels:
            # zastosowanie odpoweidnich metod wewnętrznych w zależności od zakładki
            if cat in ["kraj", "swiat", "tylko-w-onecie", "religia", "pilka-nozna", "skoki-narciarskie", "formula-1",
                       "tenis", "kolarstwo"]:
                scrape_onet_news_and_sport(cat)
            else:
                scrape_onet_regional(cat)
        # posortowanie notatek z Onetu od najnowszej do najstarszej
        self.press_notes["onet"] = self.sort_notes_by_date(onet_news)

    def scrape_wp(self):
        """ Metoda wychwytująca informacje o notatkach prasowych z kodu html Wirtualnej Polski """
        wp_news = self.press_notes["wp"]  # pobranie aktualnego zbioru notatek z WP

        def scrape_wp_news(category):
            """ Metoda wewnętrzna, pobierająca dane o artykułach ze strony 'wiadomosci.wp.pl'; artykuły na tamtejszych
            zakładkach są ułożone jak 'kafelki'; category - sktualnie badana kategoria """
            # pobranie całej zawartości html ze strony
            url = "https://wiadomosci.wp.pl/" + category
            soup = self._get_soup(url)
            # wyodrębnienie elementów, zawierających odnośniki do kolejnych artykułów
            article_anchors = soup.find_all("a", {"class": "a2PrHTUx"})
            # iteracja po notatkach (wyodrębninych elementach)
            for anchor in article_anchors:
                # wychwycenie i obsługa błędu, na wypadek gdyby format strony był niezgodny z obsługiwanym przez system
                try:
                    # pobranie i uzupełnienie linku do oryginalnego artykułu
                    # (w kodzie html dla wp odnośniki do niektórych artykułów nie posiadają nagłówków)
                    art_url = anchor.get("href")
                    if art_url[:7] != "https:/" and art_url[:6] != "http:/":
                        art_url = "https://wiadomosci.wp.pl" + art_url
                    # pobranie zawartości strony z artykułem na podstawie jego URL
                    soup2 = self._get_soup(art_url)
                    # zakładka 'koronawirus' zawiera notatki, pochodzące z różnych platform; program obsługuje 3 z nich
                    # w tym właśnie WP
                    # wyodrębnienie tytułu, lead'u i daty publikacji w zależności od strony źródłowej
                    if "wiadomosci.wp.pl" in str(art_url):
                        title = soup2.find("h1", {"class": "article--title a1xAmRvR"}).text.strip()
                        # sprawdzenie, czy artykuł nie ma specyficznego formatu, charakterystycznego dla "WP magazyn"
                        wp_magazine_href = soup2.find("div", {"data-st-area": "article-header"}).find("a").get("href")
                        if wp_magazine_href == "https://magazyn.wp.pl":
                            lead = soup2.find("div", {"class": "article--lead a3x6fdyf"}).text.strip()
                        else:
                            lead = soup2.find("div", {"class": "article--lead a1HGmjUl"}).text.strip()
                        art_date = soup2.find("div", {"data-st-area": "article-header"}).find("time").get("datetime")[:16]
                    elif "money.pl" in str(art_url):
                        title = soup2.find("h1", {"class": "sc-dNLxif sc-jqCOkK ewwpFG"}).text.strip()
                        lead = soup2.find("div", {"class": "sc-dNLxif sc-jqCOkK sc-gqPbQI iqrGbW"}).find_all("p")[1].text.strip()
                        art_date = soup2.find("div", {"class": "sc-dNLxif bHedCF"}).find("time").get("datetime")[:16]
                    elif "o2.pl" in str(art_url):
                        title = soup2.find("h1", {"class": "sc-hZSUBg sc-cMhqgX gwUZyd"}).text.strip()
                        lead = soup2.find("div", {"class": "sc-hZSUBg sc-cMhqgX sc-iuJeZd fxjjeh"}).find_all("p")[1].text.strip()
                        art_date = soup2.find("div", {"class": "sc-hZSUBg lfrejV"}).find("time").get("datetime")[:16]
                    # pominięcie iteracji i przejście do następnej notatki, jeżeli pętla natknie się na inną stronę
                    # źródłową, niż ustalone (pozostałe wymagałyby wyszukiwania elementów html o innych wartościach atrybutów)
                    else:
                        continue
                    # weryfikacja tytułu i daty, analogicznie do poprzednich metod
                    title_repeats = self._check_if_title_repeats(wp_news, title, category)
                    if title_repeats == "YES":
                        break
                    elif title_repeats == "MAYBE":
                        continue
                    art_date = art_date.replace("T", " ")
                    if self.check_if_article_is_too_old(art_date):
                        break
                    # zapisanie danych o notatce prasowej i umieszczenie jej w zbiorze artykułów dla WP
                    pressnote_info = {"Tytuł": title, "Opis": lead, "Data": art_date, "URL": art_url, "Zakladka": category}
                    wp_news[title] = pressnote_info
                except AttributeError:
                    continue

        def scrape_wp_sport(category):
            """ Metoda wewnętrzna, pobierająca dane o artykułach ze strony 'sportowefakty.wp.pl'; artykuły na tamtejszych
            zakładkach są ułożone w formie listy; category - sktualnie badana kategoria """
            # pobranie całej zawartości ze strony
            url = "https://sportowefakty.wp.pl/" + category
            soup = self._get_soup(url)
            # wyodrębnienie 'bloku' z poszukiwanymi artykułami; w zakładce 'kolarstwo' ma on inną nazwę w html-u
            if category == "kolarstwo":
                articles_section = soup.find("div", {"class": "column grid-wx2"})
            else:
                articles_section = soup.find("div", {"class": "column grid-wx0a1"})
            # wyodrębnienie poszczególnych 'bloczków' z notatkami prasowymi
            articles = articles_section.find_all("li", {"class": "streamshort streamshort--news"})
            # iteracja po kolejnych notatkach
            for note in articles:
                # wychwycenie i obsługa błędu, na wypadek gdyby format strony był niezgodny z obsługiwanym przez system
                try:
                    # wyodrębnienie linku do oryginalnego artykułu z 'bloczka' i uzupełnienie nagłówka
                    art_url = note.find("a").get("href")
                    if art_url[:7] != "https:/":
                        art_url = "https://sportowefakty.wp.pl" + art_url
                    # pobranie zawartości strony notatki prasowej na podstawie jej URL
                    soup2 = self._get_soup(art_url)
                    # pobranie informacji o tytule, lead'ie i dacie publikacji oraz weryfikacja
                    # (analogicznie do poprzednich metod)
                    title = soup2.find("h1", {"class": "title"}).text.strip()
                    title_repeats = self._check_if_title_repeats(wp_news, title, category)
                    if title_repeats == "YES":
                        break
                    elif title_repeats == "MAYBE":
                        continue
                    lead = soup2.find("span", {"class": "h5"}).text.strip()
                    art_date = soup2.find("address", {"class": "indicator"}).find("time", {"class": "indicator__time"}).get("datetime")[:16]
                    if self.check_if_article_is_too_old(art_date):
                        break
                    # zapisanie danych o notatce i umieszczenie jej w zbiorze notatek prasowych dla WP
                    pressnote_info = {"Tytuł": title, "Opis": lead, "Data": art_date, "URL": art_url, "Zakladka": category}
                    wp_news[title] = pressnote_info
                except AttributeError:
                    continue

        # właściwa część metody 'scrape_wp'; iteracja po kolejnych ustalonych zakładkach
        for cat in self.wp_labels:
            # zastosowanie odpowiednich metod wewnętrznych w zależności od zakładki
            if cat in ["pilka-nozna", "zimowe", "tenis", "moto", "kolarstwo"]:
                scrape_wp_sport(cat)
            else:
                scrape_wp_news(cat)
        # sortowanie notatek prasowych dla WP od najnowszej do najstarzej
        self.press_notes["wp"] = self.sort_notes_by_date(wp_news)

