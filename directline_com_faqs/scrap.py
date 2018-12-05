'''
This file scraps questions and answers from www.directline.com/faqs
'''

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd

# Open Firefox browser and go to the page
driver = webdriver.Firefox( executable_path="C:\\geckodriver.exe" )
driver.get( 'https://www.directline.com/faqs' )

# click view button and show all pages
driver.find_element_by_link_text('View more questions for all areas').click()
time.sleep(3)
soup = BeautifulSoup( driver.page_source, 'html.parser' )

# initialize data array
result = []

def do_page(page_no):
    '''
    Function which processes each page
    '''
    
    # if page_no is 1, page already has opened
    # else open the page
    if page_no > 1:
        driver.find_element_by_link_text(str(page_no)).click()
        time.sleep(1)
    
    # get page content
    soupp = BeautifulSoup( driver.page_source, 'html.parser' )
    
    faqs = soupp.find_all('dd', 'accordion-navigation track-faq-click ng-scope')
    print('page ' + str(page_no) + ': ' + str(len(faqs)) + ' items found')
    
    # scrap all QnA
    no = 1
    for faq in faqs:
        items = faq.find_all('p', 'ng-binding')
        index = 0
        answer = ''
        question = ''
        for item in items:
            if index == 0:
                question = item.text
            else:
                answerps = item.find_all('p')
                for p in answerps:
                    answer = answer + p.text
                    answer = answer + '\n'
            index = index + 1
        
        # eliminate the tailing newline
        answer = answer[:-1]
        result.append({'page' : page_no, 'question': question, 'answer': answer})
        no = no + 1

# scrap all pages
for i in range(1, 69):
    do_page(i)

# write to an xlsx file
df = pd.DataFrame( result, columns=['page', 'question', 'answer'] )
writer = pd.ExcelWriter( "D:\\result.xlsx", engine='xlsxwriter' )
df.to_excel( writer, 'FAQ', index=False )
writer.save()
