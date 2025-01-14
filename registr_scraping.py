# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 14:30:51 2024

@author: jmich
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd



def vytvor_adresar(path):
    """
    Funkce vytvoří aadresář.
    """
    try:
        # Vytvoření adresáře
        os.mkdir(path)
        print(f"Adresář '{path}' byl vytvořen.")
    except FileExistsError:
        print(f"Adresář '{path}' již existuje.")
    except (ValueError, KeyError) as exc:  # Handle specific error
        print(f"ValueError or KeyError occurred: {exc}")
    except TypeError as exc:
        print(f"TypeError occurred: {exc}")

def prejmenuj_smlouvu(download_path, original_filename, new_filename, \
                      string_of_downloaded_file):
    """
    Funkce, která na vstupu bere adresář stahování, cestu k původnímu souboru,
    cestu, jak se to má uložit a ještě řetězec jměna staženého souboru.
    Funkce přejmenuje soubor.
    """
    con = True
    k = 0
    while con:
        if os.path.exists(original_filename):
            if os.path.exists(new_filename):
                os.remove(new_filename)

            os.rename(original_filename, new_filename)
            print(f"Soubor byl přejmenován na {new_filename}")
            con = False
        else:
            time.sleep(5)
            k += 1
            if k > 3:
                print("Soubor nebyl nalezen")
                con = False
                for soubor in os.listdir(download_path):
                    if soubor.startswith(string_of_downloaded_file[:3]) \
                        and not os.path.exists(new_filename):
                        # Najde soubor, který začíná zadaným textem
                        original_filename = os.path.join(download_path, soubor)
                        os.rename(original_filename, new_filename)  # Přeměnuje soubor
                        print(f"Soubor {soubor} byl přejmenován na {new_filename}")



def exists_file_with_prefix(directory, prefix):
    """
    Funkce, která vrací pravdivostní hodnotu - zda existuje soubor v adresáři
    s určitou předponou.
    """
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            return True
    return False


def nacti_data_z_tabulky_path(tabulky_path):
    """
    Načte data.
    """
    if os.path.exists(tabulky_path):
        datafile = pd.read_csv(tabulky_path)
        odberatel_list = datafile["Odběratel"].to_list()
        id_smlouvy_list = datafile["ID"].to_list()
        ico_list = datafile["IČO"].to_list()
        datum_uzavreni_list = datafile["Datum uzavření smlouvy"].to_list()
        cena_bez_dph_list = datafile["Cena_bez_dph"].to_list()
        cena_s_dph_list = datafile["Cena_s_dph"].to_list()
        predmet_smlouvy_list = datafile["Předmět smlouvy"].to_list()
        id_verze_list = datafile["ID verze"].to_list()

    else:
        odberatel_list = []
        id_smlouvy_list = []
        ico_list = []
        datum_uzavreni_list = []
        cena_bez_dph_list = []
        cena_s_dph_list = []
        predmet_smlouvy_list = []
        id_verze_list = []
    return odberatel_list, id_smlouvy_list, ico_list, datum_uzavreni_list,\
    cena_bez_dph_list, cena_s_dph_list, predmet_smlouvy_list,id_verze_list

def vypsani_dat_z_hlavicky_detailu(driver):
    """
    Ziskani dat z hlavičky v detailu registru
    """
    continuing = True
    j = 1
    while continuing:
        try:
            element = driver.find_element(By.XPATH, \
    '/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[1]')
            if element:
                if element.text == "Název subjektu:":
                    odberatel = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "ID verze:":
                    id_verze = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "ID smlouvy:":
                    id_smlouvy = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "IČO:":
                    ico = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "Datum uzavření:":
                    datum_uzavreni = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "Hodnota bez DPH:":
                    cena_bez_dph = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "Hodnota vč. DPH:":
                    cena_s_dph = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
                elif element.text == "Předmět smlouvy:":
                    predmet_smlouvy = driver.find_element(By.XPATH, \
'/html/body/section/div/div[2]/div/div[1]/div[' + str(j) + ']/span[2]').text
            else:
                continuing = False
            j += 1
        except NoSuchElementException:
            continuing = False
    return odberatel, id_verze, id_smlouvy, ico, datum_uzavreni, cena_bez_dph, \
        cena_s_dph, predmet_smlouvy


def stahni_soubory_a_prejmenuj(driver, download_path, id_smlouvy):
    """
    Najdi a klikni na tlačítka pro stažení souboru, klikni na něj
    vypiš jméno souboru, přejmenuj soubor podle id smlouvy
    """
    stahnout_buttons = driver.find_elements(By.XPATH, \
                        "//a[contains(@href, 'smlouva/soubor')]")
    time.sleep(1)
    if not exists_file_with_prefix(download_path, id_smlouvy):
        for index, stahnout_btn in enumerate(stahnout_buttons):
            string_of_downloaded_file = stahnout_btn.text

            stahnout_btn.click()
            time.sleep(2)

            #vypsání jména souboru a přejmenování souboru - muže být funkce
            last_dot_index = string_of_downloaded_file.rfind(".")
            #file_name = string_of_downloaded_file[:last_dot_index]
            file_extension = string_of_downloaded_file[last_dot_index:]

            string_of_new_file = id_smlouvy + "_" + str(index) + file_extension

            original_filename = os.path.join(download_path,\
                                             string_of_downloaded_file)
            new_filename = os.path.join(download_path, string_of_new_file)

            prejmenuj_smlouvu(download_path, original_filename, \
                              new_filename, string_of_downloaded_file)



def scrape_data_from_register(dodavatel_file_name, dodavatel_ico):
    """ Podle IČO se otevře odpovídající stránka v registru smluv,
    jednotlivě se prochází záznamy - ty se otevírají v novém okně. 
    Pokud není záznam již v dokumentu,
    tak se vyčtou textové informace z tabulky, stáhnou se všechny odpovídající
    dokumenty ze smlouvy a ty se přejmenují podle id_smlouvy. Zavře se nové
    okno. Pokud již nejsou záznamy na stránce, překlikne se na další stránku.
    """
    # Nastavení cesty pro stahování
    #
    # Cesta k adresáři, který chcete vytvořit
    download_path = "stažená_data"
    vytvor_adresar(download_path)

    download_path = os.path.join("stažená_data", dodavatel_file_name + "_file")
    vytvor_adresar(download_path)
    current_directory = os.getcwd()
    download_path = os.path.join(current_directory,"stažená_data",\
                                 dodavatel_file_name + "_file")

    # Nastavení ChromeOptions pro automatické stahování
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_path,  # Cesta ke složce pro stahování
        "download.prompt_for_download": False,  # Vypnutí dialogu pro potvrzení stahování
        "download.directory_upgrade": True,  # Povoluje přepis složky stahování
        "safebrowsing.enabled": True  # Povolení stahování prohlížečem
        }
    chrome_options.add_experimental_option("prefs", prefs)

    # Inicializace prohlížeče s přizpůsobenými nastaveními
    driver = webdriver.Chrome(options=chrome_options)

    # Otevři stránku
    driver.get("https://smlouvy.gov.cz/vyhledavani?party_idnum=" + dodavatel_ico)
    time.sleep(2)  # Počkej na načtení stránky

    #načtení 500 záznamů na stránku
    element = driver.find_element(By.XPATH, '//*[@id="snippet-searchResultList-list"]/ul/li[10]')
    element.click()


    time.sleep(2)  # Počkej na načtení stránky

    pokracuj = True
    current_directory = os.getcwd()
    tabulky_path = os.path.join(current_directory,"stažené_tabulky")
    vytvor_adresar(tabulky_path)

    tabulky_path = os.path.join(tabulky_path,"Data_" + dodavatel_file_name + ".csv")
    odberatel_list, id_smlouvy_list, ico_list, datum_uzavreni_list,\
    cena_bez_dph_list, cena_s_dph_list, predmet_smlouvy_list,id_verze_list = \
        nacti_data_z_tabulky_path(tabulky_path)

    i = 0
    while pokracuj:
        # Najdi všechny tlačítka "Detail"
        detail_buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn")

        # Projdi každé tlačítko "Detail" a klikni na něj - stáhne se soubor, jméno souboru se vypíše
        for index, _ in enumerate(detail_buttons):
            detail_buttons_1 = driver.find_elements(By.CSS_SELECTOR, "a.btn")
            button = detail_buttons_1[index]

            # Pomocí JavaScriptu otevřete odkaz v novém tabu
            driver.execute_script("window.open(arguments[0].href, '_blank');",\
                                  button)

            # Přepnutí do nového tabu
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)  # Počkej na načtení detailu
            odberatel, id_verze, id_smlouvy, ico, datum_uzavreni, cena_bez_dph, \
                cena_s_dph, predmet_smlouvy = vypsani_dat_z_hlavicky_detailu(driver)

            if int(id_smlouvy) not in id_smlouvy_list:
                odberatel_list.append(odberatel)
                id_smlouvy_list.append(id_smlouvy)
                ico_list.append(ico)
                datum_uzavreni_list.append(datum_uzavreni)
                cena_bez_dph_list.append(cena_bez_dph)
                cena_s_dph_list.append(cena_s_dph)
                predmet_smlouvy_list.append(predmet_smlouvy)
                id_verze_list.append(id_verze)

            stahni_soubory_a_prejmenuj(driver, download_path, id_smlouvy)

            # Vrať se na hlavní stránku
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)  # Počkej na načtení seznamu zpět
            data = {"Odběratel": odberatel_list, "ID": id_smlouvy_list,
                "IČO": ico_list, "Datum uzavření smlouvy": datum_uzavreni_list, 
            "Cena_bez_dph": cena_bez_dph_list, "Cena_s_dph": cena_s_dph_list, 
            "Předmět smlouvy": predmet_smlouvy_list, "ID verze": id_verze_list}
            data = pd.DataFrame(data)

            data.to_csv(tabulky_path)

        time.sleep(5)
        element = driver.find_element(By.XPATH, \
        '//*[@id="snippet-searchResultList-list"]/ul/li[' + str(int(5 + i)) + ']/a')
        if element and element.text == "Následující ❯":
            element.click()
            time.sleep(5)
        else:
            pokracuj = False
        i += 1
        i = min(i, 6)
    # Zavři prohlížeč
    driver.quit()
