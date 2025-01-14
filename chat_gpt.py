# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 17:34:00 2025

@author: jmich
"""
import glob
import json
import os
import openai
from docx import Document as DD
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from win32com.client import Dispatch
import pandas as pd
from docx2pdf import convert
from striprtf.striprtf import rtf_to_text
from registr_scraping import vytvor_adresar

def extract_text_from_file(filepath):
    """Extrahuje text z různých typů souborů."""
    if filepath.endswith('.txt'):
        text = ''
        with open(filepath, 'r', encoding='ansi') as file:
            text = file.read()
        print(text)
        return text

    if filepath.endswith('.docx'):
        doc = DD(filepath)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    if filepath.endswith('.pdf'):
        images = convert_from_path(filepath)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image, lang='ces')
        print("Text:", text)
        return text
    if filepath.endswith('.rtf'):
        with open(filepath, "r", encoding="utf-8") as file:
            rtf_content = file.read()
        # Convert RTF to plain text
        plain_text = rtf_to_text(rtf_content)
        return plain_text
    if filepath.endswith('.doc'):
        word = Dispatch("Word.Application")
        doc = word.Documents.Open(filepath)
        text = doc.Content.Text
        doc.Close()
        word.Quit()
        return text

    if filepath.endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(filepath)
        return pytesseract.image_to_string(image, lang='ces')
    raise ValueError(f"Nepodporovaný typ souboru: {filepath}")

def extract_information_from_text_1(text):
    """Použije GPT k extrakci informací ze zadaného textu."""
    prompt = (
        "Analyzujte následující text a extrahujte informace pouze pokud jsou \
            uvedeny maximálně jednou - nechci duplicity. Pokud není přesné \
                množství uvedeno, dej hodnotu null "
        "1. Objednané zboží, "
        "2. Množství, "
        "3. Jednotkovou cenu bez DPH, "
        "4. Jednotkovou cenu s DPH.\n\n"
        "Text:\n" + text + "\n\n"
        "Odpověď musí být ve formátu JSON: {\"zboží\": [{\"název\": \"\",\
            \"množství\": 0, \"cena bez DPH\": -, , \"cena s dph\": -}]}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Nebo "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4"
            messages=[
                {"role": "system", "content": "Jste asistent, který analyzuje \
                 text a generuje výstupy ve formátu JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.1
        )
        result = response['choices'][0]['message']['content'].strip()
        return result
    except Exception as exc:
        print(f"Chyba při volání OpenAI API: {exc}")
        return "{}"

def extract_information_from_text_2(text):
    """Použije GPT k extrakci informací ze zadaného textu."""
    prompt = (
        "Analyzujte následující text a extrahujte informace pouze pokud jsou \
            uvedeny maximálně jednou - nechci duplicity. Pokud není přesné \
                množství uvedeno, dej hodnotu null "
        "1. Objednané zboží, "
        "2. Množství, "
        "3. Jednotkovou cenu bez DPH, "
        "4. Jednotkovou cenu s DPH.\n\n"
        "Text:\n" + text + "\n\n"
        "Odpověď musí být ve formátu JSON: {\"zboží\": [{\"název\": \"\", \
            \"množství\": 0, \"cena bez DPH\": -, , \"cena s dph\": -}]}")
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",  # Nebo "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4"
            messages=[
                {"role": "system", "content": "Jste asistent, \
                 který analyzuje text a generuje výstupy ve formátu JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens = 4096,
            temperature = 0.1
        )
        result = response['choices'][0]['message']['content'].strip()
        return result
    except Exception as exc:
        print(f"Chyba při volání OpenAI API: {exc}")
        return "{}"

def process_files_1(filepaths):
    """Provede zpracování zadaných souborů."""
    extracted_texts = []

    for filepath in filepaths:
        if os.path.isfile(filepath) and filepath.endswith(('.rtf', '.txt', \
                '.docx', '.doc', '.pdf', '.ODT', '.png', '.jpg', '.jpeg')):
            try:
                text = extract_text_from_file(filepath)
                print(f"Extrahován text ze souboru: {filepath}")
                extracted_texts.append(text)
            except Exception as exc:
                print(f"Chyba při extrakci textu ze souboru {filepath}: {exc}")
        else:
            print(filepath)

    # Sloučení všech textů do jednoho
    combined_text = "\n\n".join(extracted_texts)
    print(combined_text)
    # Zpracování kombinovaného textu pomocí GPT
    extracted_data = extract_information_from_text_1(combined_text)
    return extracted_data


def process_files_2(filepaths):
    """Provede zpracování zadaných souborů."""
    extracted_texts = []

    for filepath in filepaths:
        if os.path.isfile(filepath) and filepath.endswith(('.rtf', '.txt',\
            '.docx', '.doc', '.pdf', '.ODT', '.png', '.jpg', '.jpeg')):
            try:
                text = extract_text_from_file(filepath)
                print(f"Extrahován text ze souboru: {filepath}")
                extracted_texts.append(text)
            except Exception as exc:
                print(f"Chyba při extrakci textu ze souboru {filepath}: {exc}")
        else:
            print(filepath)

    # Sloučení všech textů do jednoho
    combined_text = "\n\n".join(extracted_texts)
    print(combined_text)
    # Zpracování kombinovaného textu pomocí GPT
    extracted_data = extract_information_from_text_2(combined_text)
    return extracted_data

def extraction_data_gpt(dodavatel_file_name, chatgpt_api_key):
    """
    Hlavní funkce, která extrahuje data, pošle na to ChatGPT a uloží je do souboru. 
    """
    # Nastavení API klíče pro OpenAI
    openai.api_key = chatgpt_api_key

    # Cesta k Tesseract OCR, pokud není automaticky detekováno
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    current_directory = os.getcwd()
    tabulky_path = os.path.join(current_directory,"stažené_tabulky")
    vytvor_adresar(tabulky_path)

    tabulky_path = os.path.join(tabulky_path,"Data_" + dodavatel_file_name + ".csv")

    data_file = pd.read_csv(tabulky_path)

    id_smluv = data_file["ID"].to_list()
    if "zboží" not in data_file.columns:
        zbozi_list = ["0" for i in range(len(id_smluv))]
    else:
        zbozi_list = data_file["zboží"].to_list()

    download_path = "stažená_data"
    vytvor_adresar(download_path)

    download_path = os.path.join("stažená_data", dodavatel_file_name + "_file")
    vytvor_adresar(download_path)
    current_directory = os.getcwd()
    download_path = os.path.join(current_directory,"stažená_data",  dodavatel_file_name + "_file")

    # Převod celé složky
    convert(download_path)

    for soubor in glob.glob(os.path.join(download_path, "*.docx")):
        os.remove(soubor)
    for i, id_smlouvy in enumerate(id_smluv):
        #print("zbozi_list[i]:", zbozi_list[i])
        if zbozi_list[i] == "0":
            filepaths = [os.path.join(download_path, soubor) for soubor in \
                    os.listdir(download_path) if \
                    os.path.isfile(os.path.join(download_path, soubor)) and \
                        soubor.startswith(str(id_smlouvy))]
            try:
                result = process_files_1(filepaths)[7:-3]
                with open('novy_soubor.txt', 'w', encoding='utf-8') as file:
                    file.write(result)
                with open('novy_soubor.txt', 'r', encoding='utf-8') as file:
                    result = file.read()
                result = json.loads(result)

                zbozi_list[i] = result["zboží"]
                print(result["zboží"])
                data_file["zboží"] = zbozi_list
                data_file.to_csv(tabulky_path, index=False)
            except Exception:
                result = process_files_2(filepaths)
                with open('novy_soubor.txt', 'w', encoding='utf-8') as file:
                    file.write(result)
                with open('novy_soubor.txt', 'r', encoding='utf-8') as file:
                    result = file.read()
                result = json.loads(result)

                zbozi_list[i] = result["zboží"]
                print(result["zboží"])
                data_file["zboží"] = zbozi_list
                data_file.to_csv(tabulky_path, index=False)
