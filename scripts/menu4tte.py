import os, fitz
from urllib.request import urlopen, urlretrieve, install_opener, build_opener
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from ftplib import FTP

from _tte import ftp_tte, schuman_auth

remove = True

ftp = FTP()
ftp.connect(ftp_tte["host"],
            ftp_tte["port"])
ftp.login(ftp_tte["user"],
          ftp_tte["passwd"])

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
    try:
        # Get menu from the website and download
        week = str(datetime.now(timezone.utc).isocalendar()[1] + 1).zfill(2)
        url_menu = f"https://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu_sainte_philomene.jpg")
    except Exception:
        # Get menu next week from the website and download
        week = str(datetime.now(timezone.utc).isocalendar()[1] + 0).zfill(2)
        url_menu = f"https://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu_sainte_philomene.jpg")

    # Connect to FTP TimeToEat and send menu file
    with open("menu_sainte_philomene.jpg", "rb") as file:
        ftp.storbinary("STOR menu_sainte_philomene.jpg", file)

    # Remove files
    if remove:
        os.remove("menu_sainte_philomene.jpg")
except Exception as e:
    print("Sainte Philomène:", e)

try:
    # Add 1 day to get next week
    menu_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    url_menu = f"https://infoconso-schuman.salamandre.tm.fr/Prod/API/public/v1/Pdf/1/1/3/{menu_date}/PDF"
    opener = build_opener()
    opener.addheaders = [("Authorization", schuman_auth)]
    install_opener(opener)
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
