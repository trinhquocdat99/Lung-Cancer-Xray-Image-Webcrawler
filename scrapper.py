from bs4 import BeautifulSoup
import re
from re import search
import urllib.request
import requests
import concurrent.futures

import time
from itertools import compress


class Scrapper:
    def __init__(self, save=False, dir=None):
        self.save = save
        self.dir = dir
        self.url = None
        self.stats = {}

    def scrape(self, url):
        self.url = url

        start = time.time()
        r = requests.get(url)   # send request to fetch website
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        images = soup.findAll('img')    # extract all image tags
        self.stats['full_load_time'] = time.time() - start
        # print("waiting for page load took: ")
        # print(self.stats['full_load_time'])

        # print(images)
        start = time.time()
        images = list(map(self.repairLinks, images))    # repair broken links

        # utilize multiple thread for faster link validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=None ) as pool:   # max_workers=None to use max threads on machine
            images_filter = list(pool.map(removeInvalidLinks, images))  # remove invalid links
        images = list(compress(images, images_filter))
        self.stats['image_processing_time'] = time.time() - start
        # print("processing image took: ")
        # print(self.stats['image_processing_time'])

        start = time.time()
        sources = soup.findAll('lazy-image')
        sources = list(map(self.repairLinks, sources))

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as pool:  # max_workers=None to use max threads on machine
            sources_filter = list(pool.map(removeInvalidLinks, sources))

        sources = list(compress(sources, sources_filter))

        self.stats['sources_processing_time'] = time.time() - start
        # print("processing other sources took: ")
        # print(self.stats['sources_processing_time'])

        regexLinkPattern = r"""\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"""
        start = time.time()
        links = re.findall(regexLinkPattern, html)  # find all link in html
        links = list(map(self.repairLinks, links))  # repair broken links
        links = list(dict.fromkeys(links))  # remove duplicate links
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as pool:  # max_workers=None to use max threads on machine
            links_filter = list(pool.map(removeInvalidLinks, links))    # remove invalid links
        links = list(compress(links, links_filter))
        self.stats['links_processing_time'] = time.time() - start
        # print("processing links took: ")
        # print(self.stats['links_processing_time'])

        # print(links)
        # print(images)
        # print(sources)

        xray_lung_images = []

        for image in images:
            xray_lung_images.append(getSrc(image))

        for source in sources:
            xray_lung_images.append(getSrc(source))

        for link in links:
            xray_lung_images.append(link)

        xray_lung_images = list(set(xray_lung_images))
        xray_lung_images = [{"url": link, "name": getImageName(link)} for link in xray_lung_images]

        # utilize multiple thread for faster link validation
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=None) as pool:  # max_workers=None to use max threads on machine
            xray_lung_images = list(pool.map(addFileSize, xray_lung_images))  # remove invalid links

        self.stats['total_file_size'] = getTotalSize(xray_lung_images)

        # save to directory
        if self.save and self.dir is not None:
            for url_ in xray_lung_images:
                urllib.request.urlretrieve(url_.get("url"), f'{self.dir}/{url_.get("name")}')

        return xray_lung_images

    def repairLinks(self, link):
        if type(link).__name__ == 'Tag' or isinstance(link, dict):  # if type of bs4 or dict
            src = getSrc(link)
            # print("\n=======")

            # print(link)
            # print(link.get('src'))
            # print("-")
            # print(src)
            # print("\n=======")

            newObj = {"alt": link.get('alt')}
            if "http" in src or 'https' in src:
                # print("link is okay")
                return link
            else:
                repaired = 'https://' + src
                if isXrayLungImage(src, link.get('alt')) and not urlExists(repaired): # if link is an xray lung image and not valid, try another repair mehtod
                    repaired = 'https://'+self.url.split('/')[2]+src
                newObj['src'] = repaired
                # print("repaired link ", newObj)
                return newObj
        else:
            if "http" in link or 'https' in link:
                return link
            else:
                repaired = 'https://' + link
                if isXrayLungImage(link, "") and not urlExists(repaired):
                    repaired = 'https://' + self.url.split('/')[2] + link
                return repaired


def removeInvalidLinks(link):
    regexImagePattern = r'(jpg|jpeg|png|image|picture)'
    if type(link).__name__ == 'Tag' or isinstance(link, dict):
        src_ = getSrc(link)
        # if src_ == "https://media.gettyimages.com/photos/broken-metal-lung-picture-id1006988894?k=6&amp;m=1006988894&amp;s=612x612&amp;w=0&amp;h=_AmuqF0mYnlk8lEat3z8QTI5pezQ2mUH9EE4yGQirlA=":
        print("\n===start====")
        print(link)
        # print(link.get('src'))
        print(src_)
        # print(type(src_))
        # print(type(link))
        print("\n===end====")
        if isinstance(src_, str) and type(search(regexImagePattern, src_.lower())).__name__ == 'Match':
            if not isXrayLungImage(src_, link.get('alt')):
                return False
            if urlExists(src_):  # if link is an image and url is valid
                print("link is valid")
                return True
            else: return False
        else: return False
    else:
        if isinstance(link, str) and type(search(regexImagePattern, link.lower())).__name__ == 'Match':
            if not isXrayLungImage(link, ""):
                return False
            if urlExists(link):  # if link is an image and url is valid
                return True
            else:
                return False
        else:
            return False


def urlExists(url, timeout=5, checkIsImage=True):
    try:
        url_ = url
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        if type(url).__name__ == 'Tag' or isinstance(url, dict): url_ = url.get('src') or url.get('data-src') or ""

        r = requests.head(url_, allow_redirects=True, timeout=timeout)
        if r.status_code == 200:
            if checkIsImage and r.headers["content-type"] in image_formats:
                return True
            elif not checkIsImage:
                return True
        else:
            return False
    except:
        return False


def isXrayLungImage(src, alt):
    pattern = '(lung|cancer|xray|x-ray|tumor)'

    # print(src)
    # print(alt)
    if isinstance(src, str) and type(search(pattern, src.lower())).__name__ == 'Match':
        print("passed")
        return True
    if isinstance(alt, str) and type(search(pattern, alt.lower())).__name__ == 'Match':
        print("passed")
        return True
    return False


def getImageName(src):
    return src.split('/')[-1].split('?')[0]

def isDataUrl(src):
    dataURLPattern = """ /^\s*data:([a-z]+\/[a-z]+(;[a-z\-]+\=[a-z\-]+)?)?(;base64)?,[a-z0-9\!\$\&\'\,\(\)\*\+\,\;\=\-\.\_\~\:\@\/\?\%\s]*\s*$/i"""
    return


def getSrc(link):
    if link.get('src') is not None:
        return link.get('src')
    if link.get('data-src') is not None:
        return link.get('data-src')

    return ""


def addFileSize(file):
    response = requests.head(file['url'], allow_redirects=True)
    size = response.headers.get('content-length', 0)
    file['size'] = size
    return file

def getTotalSize(files):
    return sum([int(file['size']) for file in files])

# scrapper = Scrapper()
# scrapper.scrape('https://www.wikidoc.org/index.php/Lung_cancer_chest_x_ray')
#
# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests')

# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests', save=True, dir="static")