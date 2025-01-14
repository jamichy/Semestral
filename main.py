# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 15:12:57 2025

@author: jmich
"""
import os
import pandas as pd
from registr_scraping import scrape_data_from_register, vytvor_adresar
from chat_gpt import extraction_data_gpt



if __name__ == "__main__":
    CHATGPT_API_KEY = "sk-proj-4UVTgFChEpBw9HTPbi3VwNIAB__1tZS-y_QXV9K1T4INc\
        7VlbVDeugsKtt4MH5EsjH4vyiOhBrT3BlbkFJsKxDidHw9mOcPpdB1J0dTUeX_Fy4Ys\
            Cc_GjaQzCRE7j0a-Pfv_KglQlf8hI1Ps3rxQPlEplBwA"

    dodavatel_file_names = ["Apos Brno", "Sucom production", "Sc professional",\
        "Lutema care", "Ramret", "Galtop", "OTEX, chráněná dílna s.r.o.", \
        "Františka Kaštylová", "družstvo TEXman", "V & V Servis CML spol. s r.o.",\
            "Zdeněk Staněk", "Polášek Holešov s.r.o."]

    dodavatel_ico_list = ["46980709", "26392496", "61171425", "17806089", \
            "08288518", "44738609", "26867524", "17661773", "22800212", \
                "47539241", "12894621", "04535111"]

    for i, dodavatel_file_name in enumerate(dodavatel_file_names):
        dodavatel_ico = dodavatel_ico_list[i]

        #Vydoluj data z registru smluv a postahuj soubory
        scrape_data_from_register(dodavatel_file_name, dodavatel_ico)

        #extrahování dat pomocí ChatGPT
        extraction_data_gpt(dodavatel_file_name, CHATGPT_API_KEY)

    list_tabulek = []
    for _, dodavatel_file_name in enumerate(dodavatel_file_names):
        current_directory = os.getcwd()
        tabulky_path = os.path.join(current_directory,"stažené_tabulky")
        vytvor_adresar(tabulky_path)

        tabulky_path = os.path.join(tabulky_path,"Data_" + dodavatel_file_name + ".csv")
        data = pd.read_csv(tabulky_path)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data["Dodavatel"] = dodavatel_file_name
        list_tabulek.append(data)

    current_directory = os.getcwd()
    tabulky_path = os.path.join(current_directory,"stažené_tabulky")
    vytvor_adresar(tabulky_path)

    tabulky_path = os.path.join(tabulky_path,"Data_vsechny.csv")
    result = pd.concat(list_tabulek, axis=0)
    result.to_csv(tabulky_path)
