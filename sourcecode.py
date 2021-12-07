# coding: utf-8 -*-
import pathlib
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import os
import re
import textwrap
import easyocr
import string
reader = easyocr.Reader(['de','en', 'pt'])
erlaubtezeichen = string.ascii_letters+string.digits
from pdf2jpg import pdf2jpg
wrapper = textwrap.TextWrapper(width=70)

def datei_auswaehlen(message='Please select Image or scanned PDF'):
    content = ''

    Tk().withdraw()
    filetypes = [
        ('PDF Files', '.pdf'), ('Images', '.jpg .png .bmp .jpeg .tif .tiff')

    ]
    datei = askopenfilename(title=message, filetypes=filetypes)
    pathlibpfad = pathlib.Path(datei)

    return pathlibpfad.suffix, str(pathlibpfad)

def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

def pdf_auslesen(inputpath, outputpath, pages='ALL'):
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, dpi=300, pages=pages)
    return result

def bildverarbeiten(suffix, inputpath):
    textdatei = inputpath.replace(suffix, '.txt')
    ganzertext = []
    result2 = reader.readtext(inputpath)
    for resu in result2:
        anhangen = resu[-2]
        anhangen = anhangen.strip()
        bindestrichamende = re.findall(r'\s*[-–]+\s*$', anhangen)
        if not any(bindestrichamende):
            anhangen = anhangen + ' '
        if any(bindestrichamende):
            anhangen = re.sub(r'\s*[-–]+\s*$', '', anhangen)
        ganzertext.append(anhangen)
    fertigertext = ''.join(ganzertext).strip()
    var = '\n'.join(wrapper.wrap(fertigertext))
    print(f'{var}\n\nsaved to: {textdatei}\n')
    with open(textdatei, encoding='utf-8', mode='w') as f:
        f.write(fertigertext)


def pdf_datei_verarbeiten(inputpath, pagenumbers):
    outputpath = re.sub(r'\\[^\\]+$', '', inputpath)
    pdf_auslesen(inputpath, outputpath, pages=pagenumbers)
    outputdurchsuchen = outputpath + '\\' + inputpath.split('\\')[-1].replace('.pdf', '.pdf_dir')
    nachumbenennung = outputdurchsuchen.split('\\')[-1]
    neuerordnername = re.sub(fr'[^{erlaubtezeichen}]+', '_', nachumbenennung).strip('_')
    neuerordnernameganz = outputpath + '\\' + neuerordnername
    os.rename(outputdurchsuchen, neuerordnernameganz)
    allekonvertiertendateien = getListOfFiles(neuerordnernameganz)
    allekonvertiertendateien = [a for a in allekonvertiertendateien if any(re.findall(r'\.jpg$', a))]
    neuedateinamen = []
    for konvda in allekonvertiertendateien:
        originaldateiname = konvda
        ersterteil = re.sub(r'\\[^\\]+$', '', konvda)
        konvda = re.findall(r'\\([^\\]+)$', konvda)[0]
        konvda = re.sub(r'\.jpg$', '', konvda)
        konvda = re.sub(fr'[^{erlaubtezeichen}]+', '_', konvda).strip('_')
        konvda = ersterteil + '\\' + konvda + '.jpg'
        os.rename(originaldateiname, konvda)
        neuedateinamen.append(konvda)
    fuerrtfdatei = ''
    endatei = ''
    for seitenzahl, einzelneseite in enumerate(neuedateinamen):
        textdatei = re.sub(r'\.jpg\s*$', '.txt', einzelneseite)
        result2 = reader.readtext(einzelneseite)
        ganzertext = []
        for resu in result2:
            anhangen = resu[-2]
            anhangen = anhangen.strip()
            bindestrichamende = re.findall(r'\s*[-–]+\s*$', anhangen)
            if not any(bindestrichamende):
                anhangen = anhangen + ' '
            if any(bindestrichamende):
                anhangen = re.sub(r'\s*[-–]+\s*$', '', anhangen)
            ganzertext.append(anhangen)
        fertigertext = ''.join(ganzertext).strip()
        var = '\n'.join(wrapper.wrap(fertigertext))
        print(f'{var}\n\nsaved to: {textdatei}\n')

        fuerrtfdatei = fuerrtfdatei + f'''Page {seitenzahl + 1}\n{fertigertext}\n\n-------------------------------------------------------------------------\n\n'''
        endatei = textdatei
        with open(textdatei, encoding='utf-8', mode='w') as f:
            f.write(fertigertext)

    endatei = re.sub(r'(\\)(\d+_*)(.*)\.txt$', '\g<1>complete_\g<3>.txt', endatei)
    # print(endatei)
    with open(endatei, mode='w', encoding='utf-8') as f:
        f.write(fuerrtfdatei)
print(1000 * '\n')
print('Image / PDF to TXT written by Johannes Fischer www.queroestudaralemao.com.br')
print('Thanks to\nhttps://github.com/JaidedAI/EasyOCR\nhttps://github.com/pankajr141/pdf2jpg\n\nfor 99% of the work')
suffix, inputpath = datei_auswaehlen()
if suffix == '.pdf':
    pagenumbers = str(input('Page numbers (separated by comma), "ALL" for whole document'))
    pagenumbers_zahlen = re.findall(r'\d+', pagenumbers)
    if any(pagenumbers_zahlen):
        pagenumbers = ','.join(pagenumbers_zahlen).strip(',')
    elif not any(pagenumbers_zahlen):
        pagenumbers = 'ALL'
    pdf_datei_verarbeiten(inputpath, pagenumbers)
elif suffix != '.pdf':
    bildverarbeiten(suffix, inputpath)

