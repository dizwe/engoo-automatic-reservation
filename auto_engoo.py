from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
import time
import datetime
import readAndSave

def read_info(site_name):
    """Read private info"""
    info = readAndSave.read_json('id_pass.json', 'utf8')
    id, password = info[site_name]['id'], info[site_name]['password']

    return id, password

"""
def safe(f):
    def safe_f(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return float('inf')

    return safe_f

#그냥 하면 nonetype object is not callable로 감(일단 문제가 있었던가니까)
"""

def send_email_when_error_happens(error, send_to):
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(error)
    msg['subject'] = 'Failed to reserve'
    _id, _password = read_info('gmail')
    _from = _id; _to = send_to
    msg['From'] = _from; msg['To'] = _to

    try:
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(_id, _password)
        s.sendmail(_from, _to, msg.as_string())
        s.quit()
    except smtplib.SMTPAuthenticationError:  # could not log in
        print('log in fail')


def selenium_reserve(id, password, teacher_nums, date_time, send_to):
    """Reserve using selenium"""
    # phantom = webdriver.PhantomJS(r'C:\Python35\selenium\webdriver\phantomjs\bin\phantomjs.exe')
    # phantom.implicitly_wait(3)
    chrome = webdriver.Chrome(r'C:\Python35\selenium\webdriver\chromedriver\chromedriver.exe')
    chrome.implicitly_wait(3)
    driver = chrome

    # 로그인
    driver.get('https://engoo.co.kr/members/sign_in')  # url
    driver.find_element_by_name('member[email]').send_keys(id)
    driver.find_element_by_name('member[password]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="new_member"]/div[3]/div[4]/button').click() #xpath

    #예약될때까지 선생님 반복
    for teacher_num in teacher_nums:
        driver.get('https://engoo.co.kr/teachers/'+ teacher_num)
        driver.find_element_by_id(date_time).click()
        time.sleep(3) # To turn on the modal, You need to have a time sleep

        """
        #driver.execute_script('setTimeout(function(){"scroll(0, 300);"}, 3600);')
        #driver.set_page_load_timeout(10)
        #driver.set_script_timeout(3)
        # driver.execute_script('scroll(0, 300);')
        # driver.implicitly_wait(10)
        # element = WebDriverWait(driver, 10).until(
        #    EC.presence_of_element_located((By.ID, "book_img")) #이미 있는 태그였다능
        # )
        # driver.set_window_size(1440, 900) # change size of window
        driver.maximize_window()
        # driver.save_screenshot('screenshot1.png')
        print(1)
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "book_img")))
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"teacher_booked_modal\"]/div/div/div")))
        except:
            driver.save_screenshot('screenshot1.png')
        print(2)
        """ #시도들...

        try:
            driver.find_element_by_id('reserve_student_wish').send_keys('hello') # When I don't write it, unknown error happens
            #driver.find_element_by_xpath('//*[@id="ticket_btn"]').click() # ticket
            driver.find_element_by_xpath('//*[@id="reserve_id"]').click() # normal
            write_reserve_date(date_time) #write the reserved date when succeed
            return 0
        except ElementNotVisibleException: # 수업 이미 있어
            try:
                driver.find_element_by_xpath('//*[@id="notifyDialog"]/div/div/div[3]/button').click() # 더이상 예약이 불가능할때
                driver.quit()
                print('You already reserved')
                return 0
            except ElementNotVisibleException as e: #수업이 이미 있을 때. -> 다른 선생님을 바꾸기
                print(e)
                continue
            except Exception as e2: # 그 외 오류들이 날때 -> 메일 보내기
                send_email_when_error_happens(e2, send_to)

    send_email_when_error_happens('There is no class to reserve. plz check', send_to) # 다른 선생님도 다 안되었을때 -> 메일 보내기


def engoo_date_str(reserve_time):
    """retrieve the date when being available to take lessen e.g.'dt_2017-04-07_00-30-00'"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    weekday_dict = readAndSave.read_json('weekday_dict_2017-04-05_to_2020-10-04.json','utf8') # 휴일 data

    def loop_until_workday(calculating_data):
        if weekday_dict[calculating_data.strftime('%Y-%m-%d')]: #휴일이나
            return calculating_data
        else:
            return loop_until_workday(calculating_data + datetime.timedelta(days=1))

    next_day = loop_until_workday(tomorrow)
    date = next_day.strftime('%Y-%m-%d')

    return 'dt_' + date + '_' + reserve_time + '-00'


def write_reserve_date(key):
    reserved_dict = readAndSave.read_json('Did_I_reserved.json', 'utf8')
    reserved_dict[key] = True
    readAndSave.save_json(reserved_dict, 'Did_I_reserved.json', 'utf8')
    return 0


def already_reserve_tf(key):
    """check whether I reserved or not."""
    reserved_dict = readAndSave.read_json('Did_I_reserved.json', 'utf8')
    return key in reserved_dict


class AutoReserveEngoo:
    def __init__(self, teacher_num, reserve_time, send_to):
        self.id, self.password = read_info('engoo')
        self.teacher_num = teacher_num
        self.reserve_time = reserve_time
        self.send_to = send_to
    def reserve(self):
        date_time = engoo_date_str(self.reserve_time)
        if already_reserve_tf(date_time):
            return 'Already have'
        else: # If I didn't reserve
            selenium_reserve(self.id, self.password, self.teacher_num, date_time, self.send_to)

me = AutoReserveEngoo(['4621','12564','11775'],'07-30','dizwe2716@gmail.com')
me.reserve()
