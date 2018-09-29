# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import string
import argparse
import hashlib
import os
from time import strptime



def createOutputDir(dirPath):

	if not os.path.exists(dirPath):
		os.makedirs(dirPath)
	


	
	
def get_reviews(soup, ho, hotel_id, hotel_name, reviewFile):
    reviews = soup.find_all("div", class_="reviewSelector")
    count = 0
    review_info =''
    for review in reviews:
        review_object = {}
        review_id = review['data-reviewid']
        review_date = review.find("span", class_="ratingDate")['title']

        review_score = review.find("span", class_="ui_bubble_rating")['class']
        review_score = review_score[1].replace("bubble_", "")
        review_score = ".".join(review_score)

        reviewer_name = review.find("div", class_="info_text").find("div").get_text()
        try:
            reviewer_address = review.find("div", class_="userLoc").get_text()
        except AttributeError:
            reviewer_address = None

        reviewer_attributes = review.find_all("span", class_="badgetext")
        try:
            reviewer_contibution = reviewer_attributes[0].get_text()
        except IndexError:
            reviewer_contibution = None
        try:
            reviewer_helpful_votes = reviewer_attributes[1].get_text()
        except IndexError:
            reviewer_helpful_votes = None
        review_title = review.find("span", class_="noQuotes").get_text()
        review_text = review.find("div", class_="prw_reviews_text_summary_hsx").get_text()
        try:
            reviewer_stayed = review.find("div", class_="recommend-titleInline noRatings").get_text()
            reviewer_stayed = reviewer_stayed.split(", ")
            try:
                stayed = reviewer_stayed[0].replace("Stayed: ", "")
            except IndexError:
                stayed = None
            try:
                travelled_as = reviewer_stayed[1]
            except IndexError:
                travelled_as = None
        except AttributeError:
            stayed = None
            travelled_as = None
            reviewer_stayed = None

        review_object['review_id'] = review_id
        review_object['review_date'] = format_date(review_date)
        review_object['review_score'] = review_score
        review_object['reviewer_name'] = reviewer_name
        review_object['reviewer_address'] = reviewer_address
        review_object['reviewer_contribution'] = reviewer_contibution
        review_object['reviewer_helpful_votes'] = reviewer_helpful_votes
        review_text =  review_text.replace("Show less", "")
        review_object['review_text'] = review_text
        review_object['review_title'] = review_title
        review_object['reviewer_stayed'] = stayed
        review_object['reviewer_travelled_as'] = travelled_as
        ho.append(review_object)
        review_info =  makeString ( hotel_id) +","+ makeString ( hotel_name) +","+ makeString (review_id)+","+   format_date( review_date )  +","+ makeString ( review_score) +","+ makeString ( reviewer_name )+","+ makeString ( reviewer_address)  +","+ makeString(reviewer_contibution) +","+ makeString(reviewer_helpful_votes)   +","+ makeString ( stayed ) +","+makeString (  travelled_as )	+","+ makeString ( review_title ) +","+ makeString ( review_text )  +"\n" 
        #review_info =  review_title +","+ review_text  +"\n"
        
        reviewFile.write(review_info)
		
        #reviewFile.close()
        count+=1

    return  count

	
	
def format_date(date_str):
    date_arr = date_str.split(' ')
    month_str = date_arr[0].strip()[:3].lower()
    
    return ( str( strptime(month_str,'%b').tm_mon ) +'/'+ date_arr[1].replace(',','')  +'/'+ date_arr[2] )
		
	
#  remove punctuation smbols BUT dont remove fullstop and comma	from input
def handle_punctuationc(s):
    #punc_list = ["-",";",":","!","?","/","\\","#","@","$","&",")","(","'","\""] # dont replace fullstop and comma
   
    new_s = ''
    for i in s:
        if i not in string.punctuation:
            new_s += i
        else:
            new_s += ' '
    return new_s
		
		
	
def makeString(s): # if None then replace ByEmptyString, if comma in then replace by ;

    if s is None:
	
        return ''
    else:
        return str(s).replace(",",";").replace("\n"," ").replace('"'," ").replace("'"," ") # replace newLine by space and comma by semicolon

		
		
def getHotelData(BASE_URL, HOTEL_URL, outputDir, hotelInfoFile):
	
    driver = webdriver.Firefox()
    driver.get(HOTEL_URL)

    more_button = driver.find_element_by_class_name("ulBlueLinks")
    if more_button:
        more_button.click()
        time.sleep(2)

    page_source = driver.page_source

    #
    # # Getting the response form the page
    # page = requests.get(BASE_URL)

    # Initialization of a hotel object
    hotel_object = {}
    hotel_object['reviews'] = []
  


    # =========================
    # html_file = open("trip_file", 'r')
    # html_file.write(page.content)
    # html_file.close()
    # =========================

    soup = BeautifulSoup(page_source, 'html.parser')

    hotel_name = makeString( soup.find(id="HEADING").get_text() )
    street_address = makeString( soup.find("span", class_="street-address").get_text() )
    locality = makeString(  soup.find("span", class_="locality").get_text()  )
    
    try:
        country = makeString(  soup.find("span", class_="country-name").get_text()  )
    except:
        country = ''

	
    address = "; ".join([street_address, locality, country])
    rating = makeString( soup.find("span", property="ratingValue")['content'])
    rank = makeString(  soup.find("b", class_="rank").get_text() )
    hotel_id =  str(  abs(hash(hotel_name)) % (10 ** 10) ) # generate a hotel ID from hotel name using hash
    
	
	
    hotel_object['name'] = hotel_name
    hotel_object['address'] = address
    hotel_object['rating'] = rating
    hotel_object['rank'] = rank.replace("#", "")
    count = 0
    print hotel_name ########################## 
   
	# write hotel reviews in a new file 
    reviewFile = open(outputDir +"/"+ hotel_name+"_"+ hotel_id +'.csv','w') # write review to file
    while True:
        time.sleep(1)
        count_obj = get_reviews(soup, hotel_object['reviews'],hotel_id, hotel_name, reviewFile)     
		
        count += count_obj
        print count,############ number of review processed
        # check the next page here
        next_button = soup.find("a", class_="next")

        if "disabled" not in next_button['class']:
            # get the next page and parse data
            url_part = next_button['href']
            driver.find_element_by_class_name("next").click()
            time.sleep(2)
            more_button = driver.find_element_by_class_name("ulBlueLinks")
            if more_button:
                more_button.click()
                time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
        else:
            break

    
	
    reviewFile.close()
	
    hotelFile = open(hotelInfoFile,'a+')	# write the basic hotel info after extracting all the reviews of the hotel
    hotel_info = hotel_id +','+ hotel_name +','+  rating  +','+  rank.replace("#", "") +','+   country  +',"'+  address +'" ,'+ str(count)+'\n'
    hotelFile.write(hotel_info) 
    hotelFile.close()
	
    print "-------------------------"
    print count
    print "----------END---------------"
	
    print hotel_info
	


if __name__ == '__main__':
	BASE_URL = 'https://www.tripadvisor.com'
	HOTEL_URL = 'https://www.tripadvisor.com/Hotel_Review-g293891-d5982537-Reviews-Hotel_Mountain_View-Pokhara_Gandaki_Zone_Western_Region.html'
	outputDir = 'reviews'
	hotelInfoFile = outputDir +'/hotelInfo.csv'
	createOutputDir(outputDir)
	

	getHotelData(BASE_URL, HOTEL_URL, outputDir, hotelInfoFile)



