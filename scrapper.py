from bs4 import BeautifulSoup
import re
from re import search
import urllib.request
import requests
import concurrent.futures

import time
from itertools import compress
from xrayClassification import isImageXray, getModelStats
from io import BytesIO
import logging

logging.captureWarnings(True)


def isXrayLungImage_(link):
    try:  # in rare cases, response might get an error, wrap in try except to avoid this
        response = requests.get(link, timeout=5, verify=False)
        img = BytesIO(response.content)
        res = isImageXray(img)
        return res
    except:
        return False


class Scrapper:
    def __init__(self, useModel=True, save=False, dir=None):
        self.save = save
        self.dir = dir
        self.url = None
        self.stats = {}
        self.useModel = useModel

    def scrape(self, url):
        self.url = url

        if self.useModel:
            self.stats['model'] = getModelStats()

        start = time.time()
        r = requests.get(url)  # send request to fetch website
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        images = soup.findAll('img')  # extract all image tags
        self.stats['full_load_time'] = time.time() - start
        self.stats['no_of_images'] = len(images)

        start = time.time()
        images = list(map(self.repairLinks, images))  # repair broken links

        # utilize multiple thread for faster link validation
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=None) as pool:  # max_workers=None to use max threads on machine
            images_filter = list(pool.map(removeInvalidLinks, images))  # remove invalid links
        images = list(compress(images, images_filter))

        self.stats['image_processing_time'] = time.time() - start

        start = time.time()
        sources = soup.findAll('lazy-image')
        self.stats['no_of_sources'] = len(sources)

        sources = list(map(self.repairLinks, sources))

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=None) as pool:  # max_workers=None to use max threads on machine
            sources_filter = list(pool.map(removeInvalidLinks, sources))
        sources = list(compress(sources, sources_filter))

        self.stats['sources_processing_time'] = time.time() - start

        regexLinkPattern = r"""\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"""
        start = time.time()
        links = re.findall(regexLinkPattern, html)  # find all link in html
        links = list(set(links))
        self.stats['no_of_links'] = len(links)
        links = list(map(self.repairLinks, links))  # repair broken links
        links = list(dict.fromkeys(links))  # remove duplicate links
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=None) as pool:  # max_workers=None to use max threads on machine
            links_filter = list(pool.map(removeInvalidLinks, links))  # remove invalid links
        links = list(compress(links, links_filter))

        self.stats['links_processing_time'] = time.time() - start

        xray_lung_images = []

        for image in images:
            xray_lung_images.append(getSrc(image))

        for source in sources:
            xray_lung_images.append(getSrc(source))

        for link in links:
            xray_lung_images.append(link)

        xray_lung_images = list(set(xray_lung_images))

        if self.useModel:
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=None) as pool:  # max_workers=None to use max threads on machine
                xray_lung_images_filter = list(pool.map(isXrayLungImage_, xray_lung_images))  # remove invalid links
            xray_lung_images = list(compress(xray_lung_images, xray_lung_images_filter))
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
        badLinkPattern = r'(.js|.php|.icon|.*com$|.gif|.pdf|.mobile)'
        if type(link).__name__ == 'Tag' or isinstance(link, dict):  # if type of bs4 or dict
            src = getSrc(link)

            newObj = {"alt": link.get('alt')}
            if len(src) < 15 or type(search(badLinkPattern, src.lower())).__name__ == 'Match':
                return link
            if "http" in src or 'https' in src:  # if link is okay
                return link
            else:  # attempt to repair link
                repaired = 'https://' + src
                if not urlExists(repaired, check_is_image=False):  # if link is not valid, try another repair method
                    repaired = 'https://' + self.url.split('/')[2] + src
                newObj['src'] = repaired
                return newObj
        else:
            if len(link) < 15 or type(search(badLinkPattern, link.lower())).__name__ == 'Match':
                return link
            if "http" in link or 'https' in link:
                return link
            else:
                repaired = 'https://' + link
                if not urlExists(repaired, check_is_image=False):
                    repaired = 'https://' + self.url.split('/')[2] + link
                return repaired

    def isXrayLungImage(self, src, alt):
        pattern = '(lung|cancer|xray|x-ray|tumor)'  # check link and slt with this regex to detect an xray iamge

        if isinstance(alt, str) and type(search(pattern, alt.lower())).__name__ == 'Match':
            return True

        if isinstance(src, str) and type(search(pattern, src.lower())).__name__ == 'Match':
            return True
        # if image cannot be detected from link and alt use ml model
        if self.useModel:
            try:  # in rare cases, response might get an error, wrap in try except to avoid this
                response = requests.get(src, timeout=5, verify=False)
                img = BytesIO(response.content)
                return isImageXray(img)
            except:
                return False
        else:
            return False


def removeInvalidLinks(link):
    regexImagePattern = r'(jpg|jpeg|png|image|images|uploads|upload|picture|photo|photos)'  # regex pattern to check if link is an image
    if type(link).__name__ == 'Tag' or isinstance(link, dict):
        src_ = getSrc(link)
        if isinstance(src_, str) and type(
                search(regexImagePattern, src_.lower())).__name__ == 'Match':  # if link is an image
            if urlExists(src_, check_is_image=False):  # if link is an image and url is valid
                return True
            else:
                return False
        else:
            return False
    else:
        if isinstance(link, str) and type(search(regexImagePattern, link.lower())).__name__ == 'Match':
            if urlExists(link, check_is_image=False):  # if link is an image and url is valid
                return True
            else:
                return False
        else:
            return False


def urlExists(url, timeout=5, check_is_image=True):  # check if the url is an image or redirects to one
    try:
        url_ = url
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        if type(url).__name__ == 'Tag' or isinstance(url, dict): url_ = getSrc(url)
        r = requests.head(url_, allow_redirects=True, timeout=timeout, verify=False)
        if r.status_code == 200 or r.status_code==405:
            if check_is_image and r.headers["content-type"] in image_formats:
                return True
            elif not check_is_image:
                return True
        else:
            return False
    except:
        return False


def getImageName(src):  # get image name from link
    return src.split('/')[-1].split('?')[0]


def isDataUrl(src):  # check if link is data url
    dataURLPattern = """^\s*data:([a-z]+\/[a-z]+(;[a-z\-]+\=[a-z\-]+)?)?(;base64)?,[a-z0-9\!\$\&\'\,\(\)\*\+\,\;\=\-\.\_\~\:\@\/\?\%\s]*\s*"""
    return bool(re.match(dataURLPattern, src))


def getSrc(link):
    if link.get('src') is not None:
        return link.get('src')
    if link.get('data-src') is not None:
        return link.get('data-src')

    return ""


def addFileSize(file):  # gets file size given url
    try:
        response = requests.head(file['url'], allow_redirects=True, timeout=5, verify=False)
        size = response.headers.get('content-length', 0)
        file['size'] = size
        return file
    except:
        file['size'] = 0
        return file


def getTotalSize(files):
    return sum([int(file['size']) for file in files])

# scrapper = Scrapper()
# scrapper.scrape('https://www.wikidoc.org/index.php/Lung_cancer_chest_x_ray')
#
# scrapper = Scrapper()
# scrapper.scrape('https://radiopaedia.org/articles/lung-cancer-3')

# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests')

# scrapper = Scrapper()
# scrapper.scrape('https://www.medicalnewstoday.com/articles/316538#tests', save=True, dir="static")
