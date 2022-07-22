from config import *
from utilities import *

from time import sleep
import pickle
import pymongo

id

def infinite_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    Noftries = 0
    while Noftries < 3:
        try:
            driver.execute_script("window.scrollBy(0, 5000);")#("window.scrollTo(0, document.body.scrollHeight);")
            
            sleep (4)

            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                Noftries += 1
            else:
                return False
        except:
            pass

    return True


def checkHeader(Header):
    myClient = pymongo.MongoClient("mongodb://localHost:27017")
    myDatabase = myClient['Twitter']
    myCollection = myDatabase['Articles']

    x = myCollection.find_one({"Header": Header})
    if x is None:
        return False
    
    return True

def WriteResult(post):
    myClient = pymongo.MongoClient("mongodb://localHost:27017")
    myDatabase = myClient['Twitter']
    myCollection = myDatabase['Articles']

    myCollection.insert_one(post)

def get_new_home_tweets(driver):
    while True:
        # infinite_scroll(driver, 1)
        driver.get(twitter_url)
        sleep(7)
        elems = driver.find_elements('class name',"css-901oao.r-18jsvk2.r-1k78y06.r-a023e6.r-16dba41.r-rjixqe.r-bcqeeo.r-bnwqim.r-qvutc0.r-1vmecro")#driver.find_elements('class name', 'css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0')


        for elem in elems:
            try:
                if checkHeader(elem.text):
                    continue
                js = {}
                js['Header'] = elem.text
                js['ArticlID'] = id
                WriteResult(js)
                id += 1
            except:
                pass

def get_tweets(driver, search_key_dic):
    global id

    for key in search_key_dic:
        url = "https://twitter.com/"
        search_key = key['search_key']
        nofTweets = key['nofTweets']

        try:
            if search_key.startswith('#'):
                url += "hashtag/"+ search_key[1:] +"?src=hashtag_click"
            else:
                url += search_key
        except Exception as e:
            print(e)

        driver.get(url)
        sleep(7)
        
        while nofTweets > 0:
            elems = driver.find_elements('css selector','div[class="css-901oao r-18jsvk2 r-1k78y06 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0 r-1vmecro"]')

            for elem in elems:
                try:
                    if checkHeader(elem.text): #can be removed 
                        continue

                    js = {}
                    js['Header'] = elem.text
                    js['ArticlID'] = id
                    WriteResult(js)

                    id += 1
                    nofTweets -= 1

                    if nofTweets <= 0:
                        break
                except:
                    pass

            if infinite_scroll(driver= driver):
                break
            sleep(2)
        pass



def get_posts_count():
    myClient = pymongo.MongoClient("mongodb://localHost:27017")
    myDatabase = myClient['Twitter']
    myCollection = myDatabase['Articles']

    return myCollection.count_documents({})

if __name__=="__main__":
    id = 700 * 1000 * 1000 + get_posts_count()
    driver = init_driver(gecko_driver, user_agent=user_agent, is_headless=headless)
    
    # login to your account
    is_login = load_cookies(driver)
    if is_login == False:
        # twitter_login(driver)\
        driver.get(twitter_login_page)
        sleep(2)
        pickle.dump(driver.get_cookies(), open(file=f".\\twitter_cookies.pkl", mode="wb"))
    
    search_key_dic = [
        {"search_key": f"AlghadNews", "nofTweets": 500}, 
        {"search_key": f"skynewsarabia", "nofTweets": 500}
    ]

    get_tweets(driver, search_key_dic)

    driver.quit()