import os, fitz
from urllib.request import urlopen, urlretrieve
from datetime import datetime
from ftplib import FTP

from _tte import ftp_tte

ftp = FTP(ftp_tte["host"],
          ftp_tte["user"],
          ftp_tte["pwd"])

# Broken for now (last working 28/06/2020) changed menu link
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
        week = str(datetime.utcnow().isocalendar()[1] + 0).zfill(2)
        url_menu = f"https://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu1.jpg")
    except:
        # Get menu next week from the website and download
        week = str(datetime.utcnow().isocalendar()[1] + 2).zfill(2)
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

ftp.close()
