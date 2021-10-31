import requests
from  selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
from datetime import timedelta, date
import smtplib, ssl
from email.mime.text import MIMEText
ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://shop.rs.berkeley.edu/booking/8e4a4640-3b33-4848-808c-4d8b03875e77/slots/dfd6cad7-3d81-48e3-b57d-49076f198dd0/"
smtp_server = "smtp.gmail.com"
port = 465  # For starttls
sender_email = "sender_email@gmail.com"
password = 'sender_email_password'
receiver_email = "phone_number_email_address"

school_user = ''
school_password = ''

selenium_cookies_s = []
# Create a secure SSL context


wanted = ['2021/08/25:7 - 8:20 PM']

# request_cookies = []

# def get_logon_cookies():
def get_cookies(date):
	try:
		driver = webdriver.Chrome()
		driver.get("https://auth.berkeley.edu/cas/login?service=https%3A%2F%2Fshib.berkeley.edu%2Fidp%2FAuthn%2FExternal%3Fconversation%3De1s1%26entityId%3Dhttps%3A%2F%2Fshop.rs.berkeley.edu%2Fshibboleth")

		username_field = driver.find_element_by_id("username")
		username_field.send_keys(school_user)

		password_field = driver.find_element_by_id("password")

		password_field.send_keys(school_password)
		password_field.send_keys(Keys.TAB)
		password_field.send_keys(Keys.ENTER)



		driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

		send_push_field = driver.find_elements_by_css_selector(".auth-button")
		trying = 0
		while (driver.title == "DuoSecurity Login - CAS – Central Authentication Service"):
			ActionChains(driver).click(send_push_field[0]).perform()
			trying +=1
			if (trying >= 1000):
				return -1
		trying = 0
		driver.get(base_url + date)
		while True:
			try:
				button_login = driver.find_elements_by_class_name("loginOption")
				ActionChains(driver).click(button_login[0]).perform()
				trying+=1
				if (trying >= 1000):
					return -1
				print("")
				if len( driver.find_elements_by_class_name("loginOption")) == 0:
					break
			except:
				print("")


		cookies = {}
		selenium_cookies = driver.get_cookies()
		selenium_cookies_s = selenium_cookies
		for cookie in selenium_cookies:
		    cookies[cookie['name']] = cookie['value']
		return cookies
	except:
		return -1



def get_info(date, r_cookies):
	print(date)
	if r_cookies == []:
		r_cookies = get_cookies(date)
	if (r_cookies == -1):
		return []
	r  = requests.get(base_url + date, cookies = r_cookies)
	soup = BeautifulSoup(r.text, 'lxml')
	table = soup.findAll('div', attrs={"class": "booking-slot-item"})
	times = [x.find('p').find('strong').text.strip() for x in table]
	availability = [x.find('span').text.strip() for x in table]
	buttons = [x.find('button').text.strip() if x.find('button') else "Not Yet Availabile" for x in table ]
	if times == [] and len(soup.findAll('div', attrs={"class": "booking-slot-not-available"})) != 1:
		r_cookies = get_cookies(date)
		if (r_cookies == -1):
			return []
	for t, a, b in zip(times, availability, buttons):
		print(t + ": " + a + ": ", b)
		if not (b == 'Not Yet Availabile' or b == 'Unavailable' or b == "Booked"):
			driver = webdriver.Chrome()
			for cookie in selenium_cookies_s:
				driver.add_cookie(cookie)
			driver.get(base_url + date)
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
				server.login(sender_email, password)
				message = date + ": " + t.strip() + ": " + a.strip()  + ": " + b.strip()
				msg = MIMEText(message, 'plain')
				server.sendmail(sender_email, receiver_email, msg.as_string())
	return r_cookies


r_cookies = []

start_date = int(input("enter offset start day: "))
end_date = start_date + int(input("enter number of days: "))




while True:
	for i in range(start_date,end_date):
		reservation_date = date.today() + timedelta(days=i)
		r_cookies = get_info(reservation_date.strftime('%Y/%m/%d'), r_cookies)

















































