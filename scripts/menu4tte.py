import os, fitz
from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
from ftplib import FTP

from _tte import ftp_tte

remove = True

ftp = FTP()
ftp.connect(ftp_tte["host"], ftp_tte["port"])
ftp.login(ftp_tte["user"], ftp_tte["passwd"])

try:
    # Get menu from the website and download
    url_static = "https://www.lycee-heinrich-nessel.fr/index.php/vivre-au-lycee/hebergement-et-restauration"
    content_page = urlopen(url_static).read()
    html = BeautifulSoup(content_page, "html.parser")
    url_menu = html.find("a", class_="uk-position-cover")["href"].replace(" ", "%20")
    urlretrieve(url_menu, "menu_heinrich_nessel.pdf")

    # Convert the menu to jpg format
    doc = fitz.open("menu_heinrich_nessel.pdf")
    pic = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    pic.save("menu_heinrich_nessel.jpg")
    doc.close()

    # Connect to FTP TimeToEat and send menu file
    with open("menu_heinrich_nessel.jpg", "rb") as file:
        ftp.storbinary("STOR menu_heinrich_nessel.jpg", file)

    # Remove files
    if remove:
        os.remove("menu_heinrich_nessel.pdf")
        os.remove("menu_heinrich_nessel.jpg")
except Exception as e:
    print("Heinrich Nessel:", e)

try:
    url_menu = "https://lycee-europeen-schuman.eu/menu.pdf"
    urlretrieve(url_menu, "menu_robert_schuman.pdf")

    # Convert the menu to jpg format
    doc = fitz.open("menu_robert_schuman.pdf")
    pic = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    pic.save("menu_robert_schuman.jpg")
    doc.close()

    # Connect to FTP TimeToEat and send menu file
    with open("menu_robert_schuman.jpg", "rb") as file:
        ftp.storbinary("STOR menu_robert_schuman.jpg", file)

    # Remove files
    if remove:
        os.remove("menu_robert_schuman.pdf")
        os.remove("menu_robert_schuman.jpg")
except Exception as e:
    print("Robert Schuman:", e)

ftp.close()

print("All menus have been sent successfully!")
