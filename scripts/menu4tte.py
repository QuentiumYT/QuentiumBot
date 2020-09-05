import os
from urllib.request import urlopen, urlretrieve
from datetime import datetime
from pdf2image import convert_from_path
from ftplib import FTP

from _tte import ftp_tte

ftp = FTP(ftp_tte["host"],
          ftp_tte["user"],
          ftp_tte["pwd"])

# Broken for now (last working 28/06/2020) changed menu link
try:
    # Get menu from the website and download
    url_static = "http://www.lyc-heinrich-haguenau.ac-strasbourg.fr/docman-documents/menus-de-la-restauration-scolaire/"
    content_page = urlopen(url_static).read()
    data_url_menu = str(content_page).split("restauration-scolaire/")[-1].split(" data-title=")[0]
    url_menu = url_static + data_url_menu
    urlretrieve(url_menu, "menu.pdf")

    # Convert the menu to jpg format
    pages = convert_from_path("menu.pdf", 500)
    for page in pages:
        page.save("menu.jpg", "JPEG")

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
        url_menu = f"http://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
        urlretrieve(url_menu, "menu1.jpg")
    except:
        # Get menu next week from the website and download
        week = str(datetime.utcnow().isocalendar()[1] + 2).zfill(2)
        url_menu = f"http://www.macantineetmoi.com/sites/default/files/etablissement/sainte-philo/sainte-philo_S{week}.jpg"
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