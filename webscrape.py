from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

base_url = 'https://www.jumia.com.eg/mobile-phones/?sort=highest-price&viewType=list&page={}#catalog-listing'

data = []

min_price = None
max_price = None

for page in range(1, 11): 
    url = base_url.format(page)
    html_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(html_page.text, 'lxml')
    mobiles = soup.find_all('a', class_='core')
    print(f"Found {len(mobiles)} mobiles on page {page}")

    for mobile in mobiles:
        try:
            # extract mobile details
            mobile_url = 'https://jumia.com.eg' + mobile['href']
            mobile_page = requests.get(mobile_url, headers=headers)
            mobile_soup = BeautifulSoup(mobile_page.text, 'lxml')

            # mobile image
            img_tag = mobile.find('img', {'data-src': True})
            mobile_img = img_tag['data-src'] if img_tag else None

            # mobile name
            name_tag = mobile.find('h3', class_='name')
            mobile_name = name_tag.text.strip() if name_tag else "No name"

            # price
            price_tag = mobile.find('div', class_='prc')
            price = price_tag.text.strip() if price_tag else "No price"
            
            try:
                price_value = float(price.replace('EGP', '').replace(',', '').strip())
                if price_value < 4000:
                    continue
            except ValueError:
                print(f"Skipping mobile with price range: {price}")
                continue
            
            company_name = mobile.get('data-gtm-brand', "No company")

            rating_tag = mobile.find('div', class_='in')
            if rating_tag:
                style = rating_tag.get('style', '')
                if 'width:' in style:
                    width_percentage = float(style.split('width:')[1].split('%')[0].strip())
                    product_rating = round((width_percentage / 100) * 5, 2)  # Convert to a rating out of 5
            else:
                product_rating = 0  # No rating

            if min_price is None or (price != "No price" and price_value < min_price):
                min_price = price_value
            if max_price is None or (price != "No price" and price_value > max_price):
                max_price = price_value

            data.append([mobile_url, mobile_name, price_value, company_name, mobile_img, product_rating])
            
            print(f"Mobile URL: {mobile_url}")
            print(f"Mobile Name: {mobile_name}")
            print(f"Price: {price_value}")
            print(f"Company Name: {company_name}")
            print(f"Image URL: {mobile_img}")
            print(f"Product Rating: {product_rating} stars")
            print()

        except Exception as e:
            print(f"Error processing mobile: {e}")
            continue

filename = f'MobilesData_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Mobile Page', 'Mobile Name', 'Price', 'Company Name', 'Mobile Image', 'Mobile Rate'])
    writer.writerows(data)

print("Done")
