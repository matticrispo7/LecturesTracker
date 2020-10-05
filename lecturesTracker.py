import os #enviroment variable
import os.path
import pandas as pd
import schedule
from datetime import datetime
import numpy
import csv, time
import smtplib #Import smtplib for the actual sending function
from email.message import EmailMessage # for building mail's messages
import schedule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions  
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager #error check

def checkFile():
    # CHECK IF FILE EXISTS
    file_exists = os.path.isfile('history.csv') 
    if file_exists:
        print("File already created\n")
    else:
        # create file
        print("creating file...")
        with open('history.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['course','lecture','date','email_sent'])
            writer.writerow([' ',' ',' ',' ']) #first empty line

def sendMail(receiver, course, title):
    #build message
    msg = EmailMessage()
    msg['Subject'] = "Lecture's published"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver
    msgBody = "Hey new lecture in " + course + " with the title " + title +" has been pusblished!"
    #TODO: modify message's body
    msg.set_content(msgBody)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        try:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("\nMail sent")
            mailSent = True
        except Exception as e:
            print(e)
            mailSent = False
    #control check for sending mail
    return mailSent

def configWebDriver():
    options = Options()
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    #load url
    driver.get(url_elly)
    time.sleep(1)
    driver.find_element_by_xpath("//*[@id=\"inst29\"]/div/div/div[1]/div/div/div[2]/div/div[1]/a/img").click() #select laurea magistrale
    time.sleep(1)
    driver.find_element_by_xpath("//*[@id=\"region-main\"]/div/div[2]/div[1]/a").click() #expand all courses
    time.sleep(1)
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div/div[2]/div[2]/div/div[7]/div[2]/div/div[1]").click() #select ing info 1 year
    time.sleep(1)
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div/div[2]/div[2]/div/div[7]/div[2]/div/div[1]/div[2]/div/div[4]/div[1]/div[1]/a").click() #select generic course
    time.sleep(1)
    #login in elly
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div/div[2]/form/fieldset/div/div/div[2]/div[1]/div/button").click() #submit button -> load page to log in
    time.sleep(1)
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div/div[2]/div[1]/a/div/div/div[2]/div/form/div[1]/div/input").click() #redirect to login page
    time.sleep(1)
    #username and password
    username = driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/form/div[1]/input")
    username.send_keys("mattia.crispino@studenti.unipr.it")
    pwd = driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/form/div[2]/input")
    pwd.send_keys(ELLY_PASSWORD)
    driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/form/div[4]/button").click()
    time.sleep(1)
    return driver

def ricercaOperativa(driver):
    ulLectures = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section[1]/div/div/ul/li[4]/div[3]/ul")
    lectures = ulLectures.find_elements_by_tag_name("li") #identify all lectures
    for i in range(len(lectures)): 
        modified_path = "/html/body/div[1]/div[3]/div/div/section[1]/div/div/ul/li[4]/div[3]/ul/li[" + str(i+1) +"]/div/div/div[2]/div[1]/a/span" #path for every lecture in the list
        #print(modified_path)
        lecture_title = driver.find_element_by_xpath(modified_path).text.splitlines()
        print(lecture_title[0])

        #read file and build DataFrame
        df = pd.read_csv('history.csv', delimiter = ',')
        
        #save current date
        date = datetime.now().strftime('%d-%m-%Y %H:%M:%S') 
        #check if lecturesDF contains lecture -> if not, insert in df
        lectures = df.lecture.to_numpy()
        if lecture_title[0] in lectures:
            print("lectures already in df")
        else:
            #lecture not found 
            print("lectures not found")
            mailSent = sendMail(EMAIL_ADDRESS, "RICERCA OPERATIVA", lecture_title[0])
            new_row = {'course':'ricerca operativa', 'lecture': lecture_title[0], 'date':date, 'email_sent': mailSent}
            #append row to df
            tempDF = df.append(new_row,ignore_index=True)
            tempDF.to_csv('history.csv', header=True, index=False)
            
    

def sistemiMultivariabili(driver):
    if(driver.find_element_by_xpath("/html/body/div[1]/nav/div/div/div/div[1]/div/button").get_attribute("aria-expanded") == "false"):
        driver.find_element_by_xpath("/html/body/div[1]/nav/div/div/div/div[1]/div/button").click() #expand sidebar
    #sidebar already expanded
    driver.find_element_by_xpath("/html/body/div[1]/div[4]/nav[2]/ul/li[10]/a").click() #select course from sidebar
    ulLectures = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section[1]/div/div/ul/li[2]/div[3]/ul")
    lectures = ulLectures.find_elements_by_tag_name("li") #identify all lectures
    #select row based on column value: df.loc[df['column'] == 'column_value']
    for i in range(len(lectures)): 
        modified_path = "/html/body/div[1]/div[3]/div/div/section[1]/div/div/ul/li[2]/div[3]/ul/li[" + str(i+1) +"]/div/div/div[2]/div[1]/a/span" #path for every lecture in the list
        lecture_title = driver.find_element_by_xpath(modified_path).text.splitlines()
        print(lecture_title[0])
        
        #read file and build DataFrame
        df = pd.read_csv('history.csv', delimiter = ',')
        
        #save current date
        date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        #check if lecturesDF contains lecture -> if not, insert in df
        lectures = df.lecture.to_numpy()
        if lecture_title[0] in lectures:
            print("lectures already in df")
        else:
            #lecture not found 
            print("lectures not found")
            mailSent = sendMail(EMAIL_ADDRESS, "SISTEMI MULTIVARIABILI", lecture_title[0])
            new_row = {'course':'sistemi multivariabili', 'lecture': lecture_title[0], 'date':date, 'email_sent': mailSent}
            #append row to df
            tempDF = df.append(new_row,ignore_index=True)
            tempDF.to_csv('history.csv',header=True, index=False)
            

'''        
def sistemiInformativi(driver):
    if(driver.find_element_by_xpath("/html/body/div[1]/nav/div/div/div/div[1]/div/button").get_attribute("aria-expanded") == "false"):
        driver.find_element_by_xpath("/html/body/div[1]/nav/div/div/div/div[1]/div/button").click() #expand sidebar
    #sidebar already expanded
    driver.find_element_by_xpath("/html/body/div[1]/div[4]/nav[2]/ul/li[9]/a").click() #select course from sidebar
    time.sleep(0.5)
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div/div/ul/li[2]/div[3]/ul/li[1]/div/div/div[2]/div[1]/a").click() #enter lectures' folder
    divLectures = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/div/section/div[1]/div[1]/div/div/div/div/div")
''' 

checkFile()

#address and password are saved as environment variable (if zsh enabled find it at .zshrc)
EMAIL_PASSWORD = os.environ['PASSWORD_MAIL']
EMAIL_ADDRESS = os.environ['ADDRESS_MAIL']
ELLY_PASSWORD = os.environ['PASSWORD_MAIL_2']
url_elly = "https://elly2020.dia.unipr.it"

def job():
    driver = configWebDriver()
    ricercaOperativa(driver)
    sistemiMultivariabili(driver)
    driver.quit()

schedule.every(90).minutes.do(job)
while True:
    try:
        schedule.run_pending()
        time.sleep(10)
    except:
        time.sleep(5)
        continue
