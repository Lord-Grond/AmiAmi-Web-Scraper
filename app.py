from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from math import ceil

app = Flask(__name__)
app.secret_key = 'cuteandfunny'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session/'
Session(app)

webdriver_path = "C:/Program Files (x86)/chromedriver-win64/chromedriver.exe"

service = Service(ChromeDriverManager().install())

chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/paulw/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("profile-directory=Default")

# dictionary format
# search_results = {"names": [], "prices": [], "ogs": [], "links": [], "tags": [], "brands": [], "dps": [], "imglinks": []}

# sorting functions
def sort_by_name(r, rev):
    if not r["names"]:
        return
    
    sorted_r = sorted(zip(r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"]), key=lambda x: x[0].lower(), reverse=rev,)
    (r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"],) =  map(list, zip(*sorted_r))


def sort_by_price(r, rev):
    if not r["prices"]:
        return

    sorted_r = sorted(zip(r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"]), key=lambda x: int(x[1].replace(",","")), reverse=rev)
    (r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"],) =  map(list, zip(*sorted_r))

def sort_by_dp(r):
    if not r["dps"]:
        return

    sorted_r = sorted(zip(r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"]), key=lambda x: "0" if x[6]=="" else x[6], reverse=True)
    (r["names"], r["prices"], r["ogs"], r["links"], r["tags"], r["brands"], r["dps"], r["imglinks"],) =  map(list, zip(*sorted_r))



@app.route('/')
def index():
    session['search_results'] = {"names": [], "prices": [], "ogs": [], "links": [], "tags": [], "brands": [], "dps": [], "imglinks": []}
    return render_template("index.html")

@app.route('/search', methods=["POST"])
def search():
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # fetch correct url depending on search and selection
    search_name = request.form.get('name')
    search_name = quote(search_name)
    base_url = "https://www.amiami.com/eng/search/list/?s_keywords=" + search_name

    pre_order = "&s_st_list_preorder_available=1"
    back_order = "&s_st_list_backorder_available=1"
    new = "&s_st_list_newitem_available=1"
    pre_owned = "&s_st_condition_flg=1"
    figure = "&s_cate_tag=1"
    bishoujo_figure = "&s_cate_tag=14"

    recently_updated = "&s_sortkey=regtimed"
    release_date = "&s_sortkey=releasedated"

    pre_order_t = request.form.get('pre-order')
    back_order_t = request.form.get('back-order')
    new_t = request.form.get('new')
    pre_owned_t = request.form.get('pre-owned')
    figure_type = request.form.get('fig')

    discount_t = request.form.get('discount')

    max_price = request.form.get('max-price')
    min_price = request.form.get('min-price')

    sort_by = request.form.get('sort-by')

    if pre_order_t:
        base_url = base_url + pre_order
    
    if back_order_t:
        base_url = base_url + back_order
    
    if new_t:
        base_url = base_url + new

    if pre_owned_t:
        base_url = base_url + pre_owned

    if figure_type == "f":
        base_url = base_url + figure
    else:
        base_url = base_url +  bishoujo_figure

    if sort_by == "recently-updated":
        base_url = base_url + recently_updated
    elif sort_by == "release-date":
        base_url = base_url + release_date

    page = 1

    # loop through all pages
    while True:
        url = base_url + f"&pagecnt={page}"
        driver.get(url)

        # wait until html is loaded
        WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading-page"))
        )
    
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.find_all("li", class_="newly-added-items__item nomore")

        # break if no more pages
        if not items:
            break

        # insert info into dict
        for item in items:
            price_tag = item.find("p", class_="newly-added-items__item__price")
            price = price_tag.contents[0].strip() if price_tag else "Price not available"

            if min_price:
                if price == "Price not available" or int(price.replace(",", "")) < int(min_price):
                    continue
            
            if max_price:
                if price == "Price not available" or int(price.replace(",", "")) > int(max_price):
                    continue

            og_price_tag = item.find("span", class_="newly-added-items__item__price_state_discount")
            og = og_price_tag.get_text(strip=True) if og_price_tag else None

            if discount_t and (not og):
                continue
            
            if og:
                dp = str(round(((1 - (float(price.replace(",", "")) / float(og.replace(",", "")))) * 100), 2)) + "%"
            else:
                dp = ""
        
            name_tag = item.find("p", class_="newly-added-items__item__name")
            name = name_tag.get_text(strip=True) if name_tag else "Name not available"

            link_tag = item.find("a")
            link = "https://www.amiami.com" + link_tag["href"] if link_tag else None

            tags = item.select("ul.newly-added-items__item__tag-list li")
            visible_tags = [tag.get_text(strip=True) for tag in tags if not tag.get("style", "").startswith("display: none")]
            if len(visible_tags) == 0:
                visible_tags = ["None"]

            brand_tag = item.find("p", class_="newly-added-items__item__brand")
            brand = brand_tag.get_text(strip=True) if brand_tag else "Brand not available" 

            imglink_tag = item.find("img")
            imglink = imglink_tag["src"] if imglink_tag and imglink_tag.has_attr("src") else "Image not available"

            session['search_results']["names"].append(name)
            session['search_results']["prices"].append(price)
            session['search_results']["ogs"].append(og if og else "")
            session['search_results']["links"].append(link)
            session['search_results']["tags"].append(visible_tags)
            session['search_results']["brands"].append(brand)
            session['search_results']["dps"].append(dp)
            session['search_results']["imglinks"].append(imglink)
        
        page += 1

    driver.quit()

    if sort_by == "name-asc":
        sort_by_name(session['search_results'], False)
    elif sort_by == "name-dsc":
        sort_by_name(session['search_results'], True)
    elif sort_by == "price-asc":
        sort_by_price(session['search_results'], False)
    elif sort_by == "price-dsc":
        sort_by_price(session['search_results'], True)
    elif sort_by == "discount-percent":
        sort_by_dp(session['search_results'])

    return redirect('/results')

@app.route('/results')
def results():
    # results page, shows 20 elements per page
    page = int(request.args.get('page', 1))
    per_page = 20

    tot_results = len(session['search_results']['names'])
    tot_pages = ceil(tot_results / per_page)

    start = (page - 1) * per_page
    end = start + per_page

    pag_res = {
        "names": session['search_results']['names'][start:end],
        "prices": session['search_results']['prices'][start:end],
        "ogs": session['search_results']['ogs'][start:end],
        "links": session['search_results']['links'][start:end],
        "brands": session['search_results']['brands'][start:end],
        "tags": session['search_results']['tags'][start:end],
        "dps" : session['search_results']['dps'][start:end],
        "imglinks" : session['search_results']['imglinks'][start:end],
    }

    return render_template("results.html", results=pag_res, page=page, tot_pages=tot_pages, zip=zip, max=max, min=min)

@app.route('/back', methods=["POST"])
def back():
    return redirect('/')

# searches for big deals (>50% off) in both new and preowned sections
@app.route('/big_deals', methods=["POST"])
def big_deals():
    driver = webdriver.Chrome(service=service, options=chrome_options)

    base_url = "https://www.amiami.com/eng/search/list/?s_cate2=459&s_st_saleitem=1&s_saleitem=1&inctxt2=2"
    go_preowned = True
    page = 1

    # seperate dicts for new and preowned in order to put all new items first
    new = {"names": [], "prices": [], "ogs": [], "links": [], "tags": [], "brands": [], "dps": [], "imglinks": []}
    preowned = {"names": [], "prices": [], "ogs": [], "links": [], "tags": [], "brands": [], "dps": [], "imglinks": []}

    while True:
        url = base_url + f"&pagecnt={page}"
        driver.get(url)
        
        WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading-page"))
        )

#        if not go_preowned:
#            driver.refresh()
#            WebDriverWait(driver, 20).until(
#            EC.invisibility_of_element_located((By.CLASS_NAME, "loading-page"))
#            )


        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.find_all("li", class_="newly-added-items__item nomore")
        

        if not items:
            if go_preowned:
                base_url = "https://www.amiami.com/eng/search/list/?s_st_condition_flg=1&s_sortkey=preowned&s_cate_tag=14"
                page = 1
                go_preowned = False
                continue
            else:
                break

        for item in items:
            price_tag = item.find("p", class_="newly-added-items__item__price")
            price = price_tag.contents[0].strip() if price_tag else "Price not available"

            og_price_tag = item.find("span", class_="newly-added-items__item__price_state_discount")
            og = og_price_tag.get_text(strip=True) if og_price_tag else None

            if not(og) or ((2 * int(price.replace(",", ""))) > int(og.replace(",", ""))):
                continue

            dp = str(round(((1 - (float(price.replace(",", "")) / float(og.replace(",", "")))) * 100), 2)) + "%"
        
            name_tag = item.find("p", class_="newly-added-items__item__name")
            name = name_tag.get_text(strip=True) if name_tag else "Name not available"

            link_tag = item.find("a")
            link = "https://www.amiami.com" + link_tag["href"] if link_tag else None

            tags = item.select("ul.newly-added-items__item__tag-list li")
            visible_tags = [tag.get_text(strip=True) for tag in tags if not tag.get("style", "").startswith("display: none")]
            if len(visible_tags) == 0:
                visible_tags = ["None"]
            if "Order Closed" in visible_tags:
                continue

            brand_tag = item.find("p", class_="newly-added-items__item__brand")
            brand = brand_tag.get_text(strip=True) if brand_tag else "Brand not available"

            imglink_tag = item.find("img")
            imglink = imglink_tag["src"] if imglink_tag and imglink_tag.has_attr("src") else "Image not available"

            if go_preowned:
                new["names"].append(name)
                new["prices"].append(price)
                new["ogs"].append(og)
                new["links"].append(link)
                new["tags"].append(visible_tags)
                new["brands"].append(brand)
                new["dps"].append(dp)
                new["imglinks"].append(imglink)
            else:
                preowned["names"].append(name)
                preowned["prices"].append(price)
                preowned["ogs"].append(og)
                preowned["links"].append(link)
                preowned["tags"].append(visible_tags)
                preowned["brands"].append(brand)
                preowned["dps"].append(dp)
                preowned["imglinks"].append(imglink)

        
        page += 1

    
    driver.close()

    # sort by discout %
    sort_by_dp(new)
    sort_by_dp(preowned)

    session['search_results']["names"].extend(new["names"])
    session['search_results']["prices"].extend(new["prices"])
    session['search_results']["ogs"].extend(new["ogs"])
    session['search_results']["links"].extend(new["links"])
    session['search_results']["tags"].extend(new["tags"])
    session['search_results']["brands"].extend(new["brands"])
    session['search_results']["dps"].extend(new["dps"])
    session['search_results']["imglinks"].extend(new["imglinks"])

    session['search_results']["names"].extend(preowned["names"])
    session['search_results']["prices"].extend(preowned["prices"])
    session['search_results']["ogs"].extend(preowned["ogs"])
    session['search_results']["links"].extend(preowned["links"])
    session['search_results']["tags"].extend(preowned["tags"])
    session['search_results']["brands"].extend(preowned["brands"])
    session['search_results']["dps"].extend(preowned["dps"])
    session['search_results']["imglinks"].extend(preowned["imglinks"])

    return redirect('/results')

"""
To Add:
-More details for figures
"""