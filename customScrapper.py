from bs4 import BeautifulSoup
import re
from re import search
import urllib.request
import requests
import concurrent.futures

import time
from itertools import compress
import pathlib
customSites = ["https://zenodo.org/record/1254210#.X8BxMc1zQal"]


class CustomScrapper:       # scrapper for extracting .mat data (not images)
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
        links = soup.findAll('a')
        self.stats['full_load_time'] = time.time() - start
        self.stats['no_of_links'] = len(links)


        links = list(map(self.repairLinks, links))    # repair broken links

        # utilize multiple thread for faster link validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=None ) as pool:   # max_workers=None to use max threads on machine
            links_filter = list(pool.map(removeInvalidLinks, links))  # remove invalid links
        links = list(compress(links, links_filter))

        self.stats['links_processing_time'] = time.time() - start

        xray_lung_data_links = []

        for link in links:
            xray_lung_data_links.append(getSrc(link))

        xray_lung_data_links = list(set(xray_lung_data_links))
        xray_lung_data_links = [{"url": link, "name": getImageName(link)} for link in xray_lung_data_links]

        # utilize multiple thread for faster link validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as pool:  # max_workers=None to use max threads on machine
            xray_lung_data_links = list(pool.map(addFileSize, xray_lung_data_links))  # remove invalid links

        self.stats['total_file_size'] = getTotalSize(xray_lung_data_links)

        # save to directory
        if self.save and self.dir is not None:
            pathlib.Path(self.dir).mkdir(parents=True, exist_ok=True)
            for url_ in xray_lung_data_links:
                urllib.request.urlretrieve(url_.get("url"), f'{self.dir}/{url_.get("name")}')
        return xray_lung_data_links

    def repairLinks(self, link):
        if type(link).__name__ == 'Tag' or isinstance(link, dict):  # if type of bs4 or dict
            src = getSrc(link)
            newObj = {"alt": link.get('alt')}
            if "http" in src or 'https' in src:
                return link
            else:
                repaired = 'https://' + src
                if isDownloadableLink(src, link.get('alt')) and not urlExists(repaired): # if link is an xray lung image and not valid, try another repair mehtod
                    repaired = 'https://'+self.url.split('/')[2]+src
                newObj['src'] = repaired
                return newObj
        else:
            if "http" in link or 'https' in link:
                return link
            else:
                repaired = 'https://' + link
                if isDownloadableLink(link, "") and not urlExists(repaired):
                    repaired = 'https://' + self.url.split('/')[2] + link
                return repaired


def removeInvalidLinks(link):
    regexImagePattern = r'(?=.*files)(?=.*download)(?=.*record)(?=.*mat)'

    if type(link).__name__ == 'Tag' or isinstance(link, dict):
        src_ = getSrc(link)
        if isinstance(src_, str) and type(search(regexImagePattern, src_.lower())).__name__ == 'Match':
            if not isDownloadableLink(src_, link.get('alt')):
                return False
            if urlExists(src_):  # if link is an image and url is valid
                print("link is valid")
                return True
            else: return False
        else: return False
    else:
        if isinstance(link, str) and type(search(regexImagePattern, link.lower())).__name__ == 'Match':
            if not isDownloadableLink(link, ""):
                return False
            if urlExists(link):  # if link is an image and url is valid
                return True
            else:
                return False
        else:
            return False


def urlExists(url, timeout=5, checkIsImage=False):
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


def isDownloadableLink(src, alt):
    pattern = r'(?=.*files)(?=.*download)(?=.*record)(?=.*mat)'
    if isinstance(src, str) and type(search(pattern, src.lower())).__name__ == 'Match':
        return True
    if isinstance(alt, str) and type(search(pattern, alt.lower())).__name__ == 'Match':
        return True
    return False


def getImageName(src):
    return src.split('/')[-1].split('?')[0]


def isDataUrl(src):
    dataURLPattern = """ /^\s*data:([a-z]+\/[a-z]+(;[a-z\-]+\=[a-z\-]+)?)?(;base64)?,[a-z0-9\!\$\&\'\,\(\)\*\+\,\;\=\-\.\_\~\:\@\/\?\%\s]*\s*$/i"""
    return


def getSrc(link):
    if link.get('href') is not None:
        return link.get('href')
    if link.get('src') is not None:
        return link.get('src')
    if link.get('data-src') is not None:
        return link.get('data-src')

    return ""


def isInCustomSites(url):
    return url in customSites


def addFileSize(file):
    response = requests.head(file['url'], allow_redirects=True)
    size = response.headers.get('content-length', 0)
    file['size'] = size
    return file


def getTotalSize(files):
    return sum([int(file['size']) for file in files])



# scrapper = CustomScrapper(save=True, dir="data")
# scrapper.scrape('https://zenodo.org/record/1254210#.X8BxMc1zQal')
#
# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests')

# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests', save=True, dir="static")