import os, fitz
from urllib.request import urlopen, urlretrieve, install_opener, build_opener
from datetime import datetime, timedelta
from ftplib import FTP

from _tte import ftp_tte, schuman_auth

ftp = FTP(ftp_tte["host"],
          ftp_tte["user"],
          ftp_tte["pwd"])

try:
    # Get menu from the website and download
    url_static = "https://www.lycee-heinrich-nessel.fr/vivre-au-lycee/hebergement-restauration/menus-de-la-restauration-scolaire/"
    content_page = urlopen(url_static).read()
    data_url_menu = str(content_page).split("restauration-scolaire/")[-1].split(" data-title=")[0]
    url_menu = url_static + data_url_menu
    urlretrieve(url_menu, "menu.pdf")

    # Convert the menu to jpg format
    doc = fitz.open("menu.pdf")
    pic = doc.loadPage(0).getPixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    pic.writePNG("menu.jpg")
    doc.close()

    # Connect to FTP TimeToEat and send menu file
    f = open("menu.jpg", "rb")
    ftp.storbinary("STOR img/menu.jpg", f)
    f.close()

    # Remove files
    os.remove("menu.pdf")
    os.remove("menu.jpg")
except Exception as e:
    print(e)

try:
    try:
        # Get menu from the website and download
        week = str(datetime.utcnow().isocalendar()[1] + 1).zfill(2)
        url_menu = f"https://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu1.jpg")
    except:
        # Get menu next week from the website and download
        week = str(datetime.utcnow().isocalendar()[1] + 0).zfill(2)
        url_menu = f"https://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu1.jpg")

    # Connect to FTP TimeToEat and send menu file
    f = open("menu1.jpg", "rb")
    ftp.storbinary("STOR img/menu1.jpg", f)
    f.close()

    # Remove files
    os.remove("menu1.jpg")
except Exception as e:
    print(e)

try:
    # Add 1 day to get next week
    menu_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    url_menu = f"https://infoconso-schuman.salamandre.tm.fr/Prod/API/public/v1/Pdf/1/1/3/{menu_date}/PDF"
    opener = build_opener()
    opener.addheaders = [("Authorization", schuman_auth)]
    install_opener(opener)
    urlretrieve(url_menu, "menu2.pdf")

    # Convert the menu to jpg format
    doc = fitz.open("menu2.pdf")
    pic = doc.loadPage(0).getPixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    pic.writePNG("menu2.jpg")
    doc.close()

    # Connect to FTP TimeToEat and send menu file
    f = open("menu2.jpg", "rb")
    ftp.storbinary("STOR img/menu2.jpg", f)
    f.close()

    os.remove("menu2.pdf")
    os.remove("menu2.jpg")
except Exception as e:
    print(e)

ftp.close()

print("All menus have been sent successfully!")
