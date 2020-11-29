
<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://xray-web-crawler.herokuapp.com/">
    <img src="static/logo560.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Crawl X-ray Image Data of Lung Cancer</h3>

  <p align="center">
    <a href="https://xray-web-crawler.herokuapp.com/">View Demo</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
        <a href="#installation">Installation</a>
    </li>
    <li><a href="#script-basic-explanation">Script Basic Explanation</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Web Crawler created using python to crawl xray lung cancer images given any url.
 The crawled data are visualized an a web interface. There is also a ```customCrawler.py``` script to download .mat files, these are also visualized on the web inference.
 Images will be identified as an xray using a simple CNN Xray classification model trained from scratch with accuracy of ```97.69```
### Built With
* [Python](https://phython.org)
* [Flask](https://palletsprojects.com/p/flask/)
* [React](https://reactjs.org)



<!-- INSTALLATION -->
## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler.git
   ```
2. Install requirements.txt
   ```sh
   pip install -r requirements.txt
   ```
3 Run app with flask
    ```sh
        python -m flask run
    ```


<!-- SCRAPPING -->
## Script Basic Explanation

### ```scrapper.py```
Main scrapping script
* Get HTML response from URL
* Extract images, links and other sources
* Setup a thread pool to run filters/repairs concurrently
* Repair broken image links and remove invalid ones
* Remove duplicates
* Filter links with regex
* Filter links that are not images
* Extract xray images using ML xray classification model
* Get image name and file size

### ```customScrapper.py```
Custom scrapping script to extract .mat files
* Get HTML response from URL
* Extract links
* Setup a thread pool to run filters/repairs concurrently
* Filter links with regex
* Remove duplicates
* Get file name and file size
Regex might need to be adjusted for other URLs



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler.svg?style=for-the-badge
[contributors-url]: https://github.com/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler.svg?style=for-the-badge
[forks-url]: https://github.com/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler/network/members
[stars-shield]: https://img.shields.io/github/stars/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler.svg?style=for-the-badge
[stars-url]: https://github.com/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Lung-Cancer-Xray-Image-Webcrawler.svg?style=for-the-badge
[issues-url]: https://github.com/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler/issues
[license-shield]: https://img.shields.io/github/license/trinhquocdat99/Lung-Cancer-Xray-Image-Webcrawler.svg?style=for-the-badge
[license-url]: https://github.com/trinhquocdat99/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/trinhquocdat99
[product-screenshot]:static/readmeImages/app.JPG
