#!/usr/bin/env python
# coding: utf-8

# In[1]:


# from selenium import webdriver
# import time
# import re


# In[192]:


# driver = webdriver.Chrome(r"C:\Users\juanr\chromedriver.exe") 
# driver.get("https://www.publicgoods.com/collections/all-products")

# SCROLL_PAUSE_TIME = 2

# # Get scroll height
# last_height = driver.execute_script("return document.body.scrollHeight")

# while True:
#     # Scroll down to bottom
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load page
#     time.sleep(SCROLL_PAUSE_TIME)

#     #Calculate new scroll height and compare with last scroll height
#     new_height = driver.execute_script("return document.body.scrollHeight")
#     print(f'Last height: {last_height}')
#     print(f'New height: {new_height}')
#     print('='*40)
#     if new_height == last_height:
#            break
#     last_height = new_height
    
# # product_name_ratings = [l.text for l in driver.find_elements_by_xpath('.//div//label[@class="collection_title all-products-product-stars"]/a')]
# products = driver.find_elements_by_xpath('.//div[@class="collection " or @class="collection"]')
# print(len(products))

# product_urls = []
# for product in products:
    
#     url = product.find_element_by_xpath('./div[@class="collection_header"]/a').get_attribute('href')
#     product_urls.append(url)


# In[193]:


# import csv
# csv_file= open("PB_Selenium_1.csv" , 'w', encoding = 'utf-8', newline = '')
# writer = csv.writer(csv_file)
# for url in product_urls:
#         driver.get(url)
#         pb_dict={}
#         #Find the elements and extract, save in dict, write to csv
#         pb_dict['product name'] = [p.text for p in driver.find_elements_by_xpath('//h1[@class="product_title"]')]
#         pb_dict['product description'] = [p.text for p in driver.find_elements_by_xpath('//div[@class="product_description"]/p')]
#         pb_dict['product volume'] = [p.text for p in driver.find_elements_by_xpath('//a[@class="subscribe-to-membership membuttonclick free stm3245"]')]
#         pb_dict['product money'] = [p.text for p in driver.find_elements_by_xpath('//span[@class="money"]')]
#         pb_dict['product key features'] = [p.text for p in driver.find_elements_by_xpath('//div[@class="spec"]')]
#         pb_dict['product rating'] = [p.text for p in driver.find_elements_by_xpath('//div[@class="yotpo-bottomline pull-left  star-clickable"]')]
#         writer.writerow(pb_dict.values())
# csv_file.close()
# driver.close()


# In[160]:


# driver.get(product_urls[0])


# In[298]:


import pandas as pd
import nltk
import re
nltk.download('punkt')
pb_df = pd.read_csv("PB_Selenium_1.csv", 
                   names=["name", "description", "volume", "cost", "key feature", "rating"])


# In[313]:


#Name of Each Product 
pb_df['name'] = [j.strip("[]").strip(" '' ") for j in pb_df['name']]


# In[314]:


replacements1 = {",": '',
                ".": '',
                "' '": '',
                "Made in ": '',
                "Product of ": '',
                "Packed in the ": '',
                "Packed in ": '',
                "Made in the  ": '',
                "Product of the ": '',
                "the ": ''}
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


# In[321]:


#Locations where products were manufactured (stills needs extra cleaning)
product_description = [j.strip("[]").strip(" '' ") for j in pb_df['description']]
lists_of_product_description = [nltk.sent_tokenize(l) for l in product_description]
pre_replace = [l[-1] for l in lists_of_product_description]
post_replace=[replace_all(l, replacements1) for l in pre_replace]
pb_df['location of manufacture'] = post_replace


# In[322]:


#Cost of Products
product_volume = [j.strip("[]").strip(" '' ") for j in pb_df['volume']]
product_cost = [j.split(" ")[2].replace("'", '').replace("$", '') for j in product_volume]
pb_df['cost']=list(map(float, product_cost))


# In[323]:


#Star Rating of Products
pre_star_rating = [j.strip('[]').replace("'", '').split() for j in pb_df['rating']]
post_star_rating= [j[1] for j in pre_star_rating]
pb_df['star rating']=list(map(float,post_star_rating))


# In[324]:


#Number of Reviews per Product
pre_number_reviews= [j.strip('[]').split() for j in pb_df['rating']]
post_number_reviews = [j[3].replace('rating\\n', '').replace('Write', '0') for j in pre_number_reviews]
pb_df['number of reviews']= list(map(int, post_number_reviews))


# In[325]:


#Core Features of Products (some elements such as 'bam boo' needs to be adjusted)
core_features = [j.strip("[]").replace('\\n', ' ') for j in pb_df['key feature']]
pb_df['core features'] = [i.lower() for i in core_features]


# In[326]:


#Volume for each Product -- Part 1
pb_df1 = pd.read_csv("PB_Selenium_1.csv", header = None)
pb_df1[2]


# In[327]:


#Volume for each Product Part 2-- self note: investigate to keep as string or convert to int or float 

replacements2 = {"'', ": '',
                "$": '',
               "oz'": 'oz',
               "ct'": 'ct',
               " capacity'": '',
               "lb'": 'lb',
               "lbs'": 'lbs'}
pre_volume=[replace_all(i, replacements2).strip('[]') for i in pb_df1[2]]
pb_df['volume']= [i[6:].strip() for i in pre_volume]


# In[722]:


# pb_df = pb_df.drop('rating', 1)


# In[328]:


#Main Ingredients of Products -- Original Description Column was delted to make pandas dataframe more succint
pre_ingredients = [j.strip('[]') for j in pb_df['description']]
def pick_only_key_sentence(str1, word):
    result = re.findall(r'([^.]*'+word+'[^.]*)', str1)
    return result
extract_ingredients = [pick_only_key_sentence(x,"'What’s in it:") for x in pre_ingredients]
ingredients_string = [str(i).strip('[]') for i in extract_ingredients]
#x = [i.strip('"\', \'What’s in it: ') for i in ingredients_string]
replacements3 = {'"\', \'What’s in it: ': '',
                 '\'", \\\'What’s in it: ': '',
                 '30% bamboo and 70% sugar cane"': 'bamboo, sugar cane',
                  '" Enjoy softer, hydrated skin without synthetic fragrance\', \'What’s in it: ': '',
                  'carefully considered high quality, natural and healthy ingredients"': '',
                  ' and ': ',',
                   '"': '',
                   "gel'": 'gel',
                   "propanol'": 'propanol',
                   ",vetiver, over 99% natural ingredients, with a small amount of high grade laboratory products to improve quality": 'vetiver',
                   " with carefully considered high quality, natural,healthy ingredients'": '',
                   " with carefully considered high quality, natural,healthy ingredients '": '',
                   " ', 'What’s in it: carefully considered high quality, natural,,healthy ingredients derived from ": '',
                   "oils'": 'oils',
                    "oil'": 'oil',
                    "adhesive'": 'adhesive',
                    "based ingredients'": "based ingredients",
                    "cotton'": 'cotton',
                    "bags'": 'bags',
                    "bamboo'": "bamboo",
                    "ash'": 'ash',
                    "(plant-derived softener)'": "(plant-derived softener)",
                    "powder'": 'powder',
                    "coconut'": "coconut",
                    "herbs'":"herbs",
                    "salmon'":'salmon',
                    "spices'": 'spices',
                    " ', 'What’s in it: ": '',
                    "tea'": 'tea',
                    "flour'": "flour",
                    ")'": ")",
                    "vanilla'": 'vanilla',
                    "flavors": "flavors",
                    "flavor'": 'flavor',
                    "salt": "salt",
                    "kernels'": 'kernels',
                    "s'": 's',
                    "catnip'": 'catnip',
                    "t'": 't',
                    "l'": 'l',
                    "y'": 'y'}
pb_df['main ingredients']=[replace_all(i, replacements3)for i in ingredients_string]
pb_df


# In[359]:


replacements4 = {'New Jersey':'Domestic', 
                'China':'International', 
                'Illinois':'Domestic', 
                'Colorado': 'Domestic', 
                'Tennessee': 'Domestic',
                'Vermont': 'Domestic', 
                'Massachusetts': 'Domestic', 
                'Mexico':'International', 
                'California':'Domestic', 
                'USA': 'Domestic', 
                'Iowa':'Domestic',
               'Arizona':'Domestic', 
                'Ohio': 'Domestic', 
                'Slovenia':'International', 
                'Canada': 'International', 
                'Turkey':'International', 
                'Oregon': 'Domestic',
                'Wisconsin':'Domestic', 
                'Australia':'International', 
                'Morocco': 'International', 
                'Italy': 'International', 
                'India': 'International', 
                'Bulgaria': 'International',
               'Washington': 'Domestic', 
                'Spain': 'International', 
                'Denmark': 'International', 
                'Brazil and Vietnam': 'International',
               'Argentina': 'International', 
                'Thailand': 'International', 
                'Lithuania': 'International', 
                'Central and South America': 'International',
               'Kentucky': 'Domestic', 
                'Georgia': 'Domestic', 
                'Ecuador': 'International', 
                'North Carolina': 'Domestic', 
                'Pakistan': 'International',
               'Vietnam': 'International',  
                'Louisiana': 'Domestic', 
                'Germany': 'International', 
                'Pennsylvania': 'Domestic',
               'New York': 'Domestic', 
                'Nebraska': 'Domestic', 
                'Missouri': 'Domestic'}

#pb_df['location of manufacture']
pb_df['location of manufacture']=[replace_all(i, replacements4)for i in pb_df['location of manufacture']]
pb_df


# In[277]:


#pb_df = pb_df.drop('description', 1)


# In[360]:


#Edit of location of manufacture 
pb_df.loc[186,'location of manufacture'] = 'Domestic'
pb_df.loc[187,'location of manufacture'] = 'Domestic and International'
pb_df.loc[188,'location of manufacture'] = 'Domestic and International'
pb_df.loc[190,'location of manufacture'] = 'International'
pb_df.loc[191,'location of manufacture'] = 'Domestic and International'
pb_df.loc[192,'location of manufacture'] = 'International'
pb_df.loc[193,'location of manufacture'] = 'Domestic and International'
pb_df.loc[194,'location of manufacture'] = 'International'
pb_df.loc[195,'location of manufacture'] = 'International'
pb_df.loc[206,'location of manufacture'] = 'International'
pb_df.loc[208,'location of manufacture'] = 'International'


# In[331]:


#Edit where location of manufacture is:
#'Please note that due to customs restrictions we cannot ship this item internationally'
pb_df.loc[5,'location of manufacture'] = 'Illinois'
pb_df.loc[6,'location of manufacture'] = 'Illinois'
pb_df.loc[7,'location of manufacture'] = 'Colorado'
pb_df.loc[8,'location of manufacture'] = 'New Jersey'
pb_df.loc[31,'location of manufacture'] = 'Massachusetts'
pb_df.loc[140,'location of manufacture'] = 'Thailand'
pb_df.loc[164,'location of manufacture'] = 'California'
pb_df.loc[165,'location of manufacture'] = 'California'
pb_df.loc[166,'location of manufacture'] = 'California'
pb_df.loc[207,'location of manufacture'] = 'Italy'
pb_df.loc[208,'location of manufacture'] = 'Italy, Spain and Greece'
pb_df.loc[210,'location of manufacture'] = 'USA'


# In[332]:


#Edit where location of manufacture is:
#USA with globally sourced components
pb_df.loc[35,'location of manufacture'] = 'USA'
pb_df.loc[36,'location of manufacture'] = 'USA'


# In[333]:


#Edit where location of manufacture is:
#USA with globally sourced components
pb_df.loc[41,'location of manufacture'] = 'China'


# In[334]:


#Edit where location of manufacture is:
#Made of agave fiber it gently exfoliates for softer more supple skin"
pb_df.loc[49,'location of manufacture'] = 'USA'


# In[335]:


#Edit where location of manufacture is:
#'Razor blades sold separately'
pb_df.loc[41,'location of manufacture'] = 'China'


# In[336]:


#Edit where location of manufacture is:
#Review CDC’s handy guide on safe mask usage here
pb_df.loc[55,'location of manufacture'] = 'China'


# In[337]:


#Edit where location of manufacture is:
#'Rid your home of unsafe toxic chemicals and upgrade to powerful plant-based formulas for all of your cleaning needs'
pb_df.loc[58,'location of manufacture'] = 'USA'


# In[338]:


#Edit where location of manufacture is:
#'It comes with a handy concentrated refill so you can reuse your spray bottle again and again'
pb_df.loc[60,'location of manufacture'] = 'USA'


# In[339]:


#Edit where location of manufacture is:
#'It comes with a handy concentrated refill so you can reuse your spray bottle again and again'
pb_df.loc[60,'location of manufacture'] = 'USA'


# In[340]:


#Edit where location of manufacture is:
#'For safest use do not burn our candles past last 1/2" of wax'
pb_df.loc[76,'location of manufacture'] = 'USA'
pb_df.loc[77,'location of manufacture'] = 'USA'
pb_df.loc[78,'location of manufacture'] = 'USA'


# In[345]:


#pb_df.to_csv('WebScraping_CleanData.csv')


# In[515]:


pb_df.describe()


# In[58]:


get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().system('pip install --upgrade nbformat')
get_ipython().system('pip install --upgrade plotly')


# In[76]:


import seaborn as sns


# In[383]:


#Appending Missing CBD Data
data = {'name': ['CBD Oil 1000mg Original', 'CBD Oil 1000mg Peppermint','CBD 20mg Softgels', 'CBD 500mg Salve'],
        'volume':['2 oz', '2 oz', '30 ct', '2 oz'],
        'cost': [90.00, 90.00, 70.00, 60.00],
        'location of manufacture':['Domestic', 'Domestic','Domestic','Domestic'],
        'star rating':[4.5, 5.0, 5.0, 5.0],
        'number of reviews':[2, 3, 2, 4],
        'core features':["'o organic', 'vf vegan friendly', 'gf gluten free', 'ng non gmo'", "'o organic', 'vf vegan friendly', 'gf gluten free', 'ng non gmo'","'o organic', 'vf vegan friendly', 'gf gluten free', 'ng non gmo'","'o organic', 'vf vegan friendly', 'gf gluten free', 'ng non gmo'"],
        'main ingredients':["'organic MCT oil, organic CBD hemp infusion'", "'regeneratively grown hemp, organic MCT oil and organic peppermint essential oil'","'regeneratively grown hemp, organic MCT oil'","'regeneratively grow hemp, organic MCT oil, organic olive oil, organic hemp seed oil, candelilla wax and organic eucalyptus essential oil'"]}
missing_cbd = pd.DataFrame(data) 
x = pb_df
pb_df = x.append(missing_cbd, ignore_index=True, sort = False)


# In[444]:


#Distribution of Location by Cost
sns.set_style("whitegrid")
loc_cost = sns.boxplot(x="location of manufacture", y="cost",
            palette=["green", "m"],
            data=pb_df[7:])
loc_cost.set(xlabel = "Location of Manufacture",ylabel ='Cost', ylim= (0,20))
plt.title('Distribution of Location by Cost')


# In[517]:


#Star Ratings vs. Number of Reviews
star_cost=sns.scatterplot(x='star rating', 
                   y = 'number of reviews',
                data = pb_df[7:],
                   color = 'blue')
star_cost.set(xlabel = "Star Rating",ylabel ='Number of Reviews')
plt.title('Star Ratings vs. Number of Reviews')


# In[521]:


#'Star Ratings vs. Price of Product'
star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = pb_df[7:],
                   color = 'g')
star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Star Ratings vs. Price of Product')


# In[386]:


#Number of Reviews vs. Price of Product
star_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = pb_df[7:],
                   color = 'm')
star_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Number of Reviews vs. Price of Product')


# In[448]:


#Prep for plots
cbd= pb_df[246:250]
pets = pb_df[231:246]
vitamins = pb_df[220:231]
grocery = pb_df[108:220]
household = pb_df[54:108]
personal_care = pb_df[6:54]
member_fav = pb_df[0:6]

#'Member Favorite: Number of Reviews vs. Price of Product'
mem_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = member_fav,
                   color = 'm')
mem_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Member Favorite: Number of Reviews vs. Price of Product')


# In[449]:


#'Member Favorite: Star Ratings vs. Price of Product'
mem_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = member_fav,
                   color = 'm')
mem_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Member Favorite: Star Ratings vs. Price of Product')


# In[416]:


#'Personal Care: Number of Reviews vs. Price of Product'
pc_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = personal_care,
                   color = 'orange')
pc_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Personal Care: Number of Reviews vs. Price of Product')


# In[502]:


#'Personal Care: Star Ratings vs. Price of Product'
pc_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = personal_care,
                   color = 'orange')
pc_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Personal Care: Star Ratings vs. Price of Product')


# In[417]:


#'Household: Number of Reviews vs. Price of Product'
hh_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = household,
                   color = 'crimson')
hh_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Household: Number of Reviews vs. Price of Product')


# In[503]:


#'Household: Star Ratings vs. Price of Product'
hh_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = household,
                   color = 'crimson')
hh_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Household: Star Ratings vs. Price of Product')


# In[421]:


#'Groceries: Number of Reviews vs. Price of Product'
gy_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = grocery,
                   color = 'green')
gy_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Groceries: Number of Reviews vs. Price of Product')


# In[514]:


#'Grocery: Star Ratings vs. Price of Product'
gy_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = grocery,
                   color = 'green')
gy_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Grocery: Star Ratings vs. Price of Product')


# In[423]:


#'Vitamins: Number of Reviews vs. Price of Product'
vt_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = vitamins,
                   color = 'brown')
vt_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Vitamins: Number of Reviews vs. Price of Product')


# In[504]:


#'Vitamins: Star Ratings vs. Price of Product'
vt_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = vitamins,
                   color = 'brown')
vt_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Vitamins: Star Ratings vs. Price of Product')


# In[425]:


#'Pets: Number of Reviews vs. Price of Product'
pt_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = pets,
                   color = 'black')
pt_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('Pets: Number of Reviews vs. Price of Product')


# In[522]:


#'Pets: Star Ratings vs. Price of Product'
pt_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = pets,
                   color = 'black')
pt_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('Pets: Star Ratings vs. Price of Product')


# In[428]:


#'CBD: Number of Reviews vs. Price of Product'
cbd_review_cost=sns.scatterplot(x='number of reviews', 
                   y = 'cost',
                data = cbd,
                   color = 'darkblue')
cbd_review_cost.set(xlabel = "Number of Reviews",ylabel ='Cost')
plt.title('CBD: Number of Reviews vs. Price of Product')


# In[441]:


#'CBD: Star Ratings vs. Price of Product'
cbd_star_cost=sns.scatterplot(x='star rating', 
                   y = 'cost',
                data = cbd,
                   color = 'darkblue')
cbd_star_cost.set(xlabel = "Star Rating",ylabel ='Cost')
plt.title('CBD: Star Ratings vs. Price of Product')


# In[512]:


#Count of Location of Manufacture for reference 
pb_df['location of manufacture'].value_counts()


# In[507]:


#Snapshot of each product category, sorted by star rating

# change_title = pb_df.copy()
# change_title.columns=['Name', 'Volume', 'Cost', 'Location of Manufacture', 'Star Rating',
#        'Number of Reviews', 'Core Features', 'Main Ingredients']
# change_title
# # cbd_titlechange= change_title[246:250]
# # cbd_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# #pets_titlechange= change_title[231:246]
# #pets_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# #vitamins_titlechange= change_title[220:231]
# #vitamins_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# #grocery_titlechange= change_title[108:220]
# #grocery_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# #household_titlechange= change_title[54:108]
# #household_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# # personal_care_titlechange= change_title[6:54]
# # personal_care_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).head(5)
# member_fav_titlechange= change_title[0:6]
# member_fav_titlechange.set_index('Name').sort_values('Star Rating', ascending=False).tail(5)

