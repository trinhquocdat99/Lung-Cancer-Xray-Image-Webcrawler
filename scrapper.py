from bs4 import BeautifulSoup
import re
from re import search
import requests



def scrape(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    images = soup.findAll('img')
    images = list(map(repairLinks, images))
    images = list(filter(removeInvalidLinks, images))

    sources = soup.findAll('lazy-image')
    sources = list(map(repairLinks, sources))
    sources = list(filter(removeInvalidLinks, sources))

    regexLinkPattern = r"""\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"""
    # links = []
    links = re.findall(regexLinkPattern, html)
    links = list(map(repairLinks, links))
    links = list(dict.fromkeys(links))
    links = list(filter(removeInvalidLinks, links))

    xray_lung_images = []

    for image in images:
        if isXrayLungImage(image.get('src'), image.get('alt')):
            xray_lung_images.append(image.get('src'))

    for source in sources:
        if isXrayLungImage(source.get('src'), source.get('alt')):
            xray_lung_images.append(source.get('src'))

    for link in links:
        if isXrayLungImage(link, ""):
            xray_lung_images.append(link)

    xray_lung_images = list(set(xray_lung_images))
    return xray_lung_images


def removeInvalidLinks(link):
    regexImagePattern = r'(jpg|jpeg|png)'
    if type(link).__name__ == 'Tag' or isinstance(link, dict):
        if re.search(regexImagePattern, link.get('src')):
            if urlExists(link.get('src')):  # if link is an image and url is valid
                return True
            else: return False
        else: return False
    else:
        if re.search(regexImagePattern, link):
            if urlExists(link):  # if link is an image and url is valid
                return True
            else:
                return False
        else:
            return False



def repairLinks(link):
    if type(link).__name__ == 'Tag' or isinstance(link, dict):
        newObj = {"alt": link.get('alt')}
        if "http" in link.get('src') or 'https' in link.get('src'):
            return link
        else:
            newObj['src'] = 'http://'+link.get('src')
            return newObj
    else:
        if "http" in link or 'https' in link:
            return link
        else:
            return 'http://'+link



def urlExists(url):
    try:
        r = requests.head(url, allow_redirects=True)
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def isXrayLungImage(src, alt):
    pattern = '(lung|cancer|xray|x-ray|tumor)'
    if search(pattern, src.lower()) or search(pattern, alt.lower()):
        return True
    else:
        return False



# scrape('https://www.medicalnewstoday.com/articles/316538#tests')