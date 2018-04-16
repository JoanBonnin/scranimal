# Animal shelters web-scraping
#### Web-scraping practice for  "Type and life -cycle of data" subject 

### by Joan Bonnín & Jose L. Dolz

## Description
The current repository is a web-scraping practice in Python for the subject "Type and life-cycle of data" for the Data Science Master Degree of the Open University of Catalonia ([UOC](http://www.uoc.com)).

The practice makes use of [Scrapy](scrapy.org), an open source and collaborative framework for extracting the data you need from websites. In this particular case, the spider crawls all active **animal shelters** that use [Bambu CMS](http://bambu-cms.org/) to **promulgate the adoption of rescued animals** and saves the data in a Comma Separated Values file (CSV).

## Execution
Just fork or download the repository and make sure you have the latest version of [Python](https://www.python.org/) and install Scrapy:

    > pip install scrapy

Then, in the *Scranimal* folder, just run the script called:

    > ./run.sh

The crawler will visit Bambu page where the active shelter using this CMS are displayed. Then, it will visit all the pages where the animals that need adoptions are listed and, afterwards, it will visit every pet profile.

If you want the data file in other format than CSV, open a prompt terminal and run the next sentence in the *Scranimal* folder:

    scrapy crawl adopting -o filename.ext -t FEED_FORMAT

Where FEED_FORMAT can be:
 - **json**
 - **jsonlines**
 - **csv**
 - **xml**
 - **pickle**
 - **marshal**

## Source code file description
The source code can be found under the *Scranimal* folder. The most important files are:

 - **scranimal/settings.py**: crawler settings, like bot name, user agent, throttle time,  number of concurrent request, logging file, etc.
 - **scranimal/spiders/adoptingSpider.py**: the crawler implementation code. Function *parse* is the main function used by Scrapy to start the crawler.

## Disclaimer
This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode) license (**Attribution-NonCommercial-ShareAlike**).

#### You are free to:

 -   **Share**  — copy and redistribute the material in any medium or format.
 -   **Adapt**  — remix, transform, and build upon the material
#### Under the following terms:
-   **Attribution**  —  You must give  [appropriate credit](https://creativecommons.org/licenses/by-nc-sa/4.0/#), provide a link to the license, and  [indicate if changes were made](https://creativecommons.org/licenses/by-nc-sa/4.0/#). You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
    
-   **NonCommercial**  — You may not use the material for  [commercial purposes](https://creativecommons.org/licenses/by-nc-sa/4.0/#).
    
-   **ShareAlike**  — If you remix, transform, or build upon the material, you must distribute your contributions under the  [same license](https://creativecommons.org/licenses/by-nc-sa/4.0/#)  as the original.
    

-   **No additional restrictions**  — You may not apply legal terms or  [technological measures](https://creativecommons.org/licenses/by-nc-sa/4.0/#)  that legally restrict others from doing anything the license permits.