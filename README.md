# AmiAmi Web Scraper
To help me look for anime figures, I made a basic web scraper for the popular anime merchandise site amiami.

## How it works
Tech Used: Python, HTML/CSS, Bootstrap, Flask, selenium
Flask is used for a web based user interface, selenium for fetching relevant HTML information from the website.

## Usage
- Basic search functionality including search bar, tags, sorting
- Included additional functions not initially in amiami site, such as sort by price/name, min/max price, discounted tag
- Improved results page by making text and pictures larger, as well as showing discount percentage
- Implemented function to search for big deals in new/pre-owned section to help my broke ass save money

## Potential Issues
Very rarely there may be some issues loading the web pages on the chrome driver, which will cause it to not work as expected. AmiAmi also does this thing where it will lock you out if there is too much web traffic, so then the loop will terminate prematurely and return an incomplete list of items (this is definitely fixable I'm just too lazy rn)

## Images
Home Page
![image](https://github.com/user-attachments/assets/f2ad1d1a-d485-4259-bad7-d6d0e377e7d9)

Results Page
![image](https://github.com/user-attachments/assets/fdb53934-42ec-41a4-939c-8b55ed636900)

Price Sorted Results Page
![image](https://github.com/user-attachments/assets/11b4fb7f-1631-46d3-b144-65d83ecc05c6)

Big Deals (new figures first then pre-owned, also sorted by discount %)
![image](https://github.com/user-attachments/assets/12f64388-af4a-4346-876d-8c7d68fa1bfc)

