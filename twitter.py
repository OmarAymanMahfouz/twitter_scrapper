from sqlalchemy import true
from config import *
from utilities import *

from time import sleep
import pickle
import pymongo
from selenium.webdriver.common.by import By

def checkTweetId(TweetId):
    myClient = pymongo.MongoClient("mongodb://localHost:27017")
    myDatabase = myClient['Twitter']
    myCollection = myDatabase['Articles']

    x = myCollection.find_one({"ArticlID": TweetId})
    if x is None:
        return False
    
    return True

def WriteResult(post):
    myClient = pymongo.MongoClient("mongodb://localHost:27017")
    myDatabase = myClient['Twitter']
    myCollection = myDatabase['Articles']

    myCollection.insert_one(post)



def get_tweets(driver, search_key_dic):

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
        
        TriesCounter = 0
        while nofTweets > 0:
            tweets = driver.find_elements(By.CSS_SELECTOR, 'div[class="css-901oao r-18jsvk2 r-1k78y06 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0 r-1vmecro"]')#driver.find_elements_by_css_selector('div[class="css-901oao r-18jsvk2 r-1k78y06 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0 r-1vmecro"]')
            linkes = driver.find_elements(By.CSS_SELECTOR, 'a[class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-1q142lx r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"]')#driver.find_elements_by_css_selector('a[class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-1q142lx r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"]')

            for (tweet, link) in zip(tweets, linkes):
                try:
                    tweet_link = str(link.get_property('href')).split('/')
                    tweet_id = int(tweet_link[-1])

                    if checkTweetId(tweet_id):
                        continue

                    js = {}
                    js['Header'] = tweet.text
                    js['ArticlID'] = tweet_id
                    WriteResult(js)

                    nofTweets -= 1
                    TriesCounter = 0


                    if nofTweets <= 0:
                        print (str(key) + " has Terminated due to nof spcified tweets has been reached")
                        break
                except:
                    pass


            driver.execute_script("window.scrollBy(0, 1500);")
            sleep(3)

            endOfPage = driver.find_elements(By.XPATH, "//div[@class='css-1dbjc4n r-o52ifk']//div[@class='css-1dbjc4n r-o52ifk']")#driver.find_elements_by_xpath("//div[@class='css-1dbjc4n r-o52ifk']//div[@class='css-1dbjc4n r-o52ifk']")
            if len(endOfPage) > 0 and TriesCounter == NofScrollingTries:
                print (str(key) + " has Terminated due to no more scrolling")
                break
            elif len(endOfPage) > 0:
                TriesCounter += 1


if __name__=="__main__":
    driver = init_driver(gecko_driver, user_agent=user_agent, is_headless=headless)

    # login to your account
    is_login = load_cookies(driver)
    if is_login == False:
        # twitter_login(driver)\
        driver.get(twitter_login_page)
        
        sleep(2)
        pickle.dump(driver.get_cookies(), open(file=f".\\twitter_cookies.pkl", mode="wb"))
        
    search_key_dic = [
        {"search_key": f"#صدى_البلد", "nofTweets": 1000},
        {"search_key": f"ElBaladOfficial", "nofTweets": 500}        
    ]

    get_tweets(driver, search_key_dic)

    driver.quit()