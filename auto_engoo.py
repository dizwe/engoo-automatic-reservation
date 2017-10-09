
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
import time
import datetime
import readAndSave
import logging
import logging.handlers
# from selenium.webdriver.common.keys import Keys
# from pyvirtualdisplay import Display
# import os

def read_id_pw(site_name):
    """Read private info"""
    info = readAndSave.read_json('id_pass.json', 'utf8')
    id, password = info[site_name]['id'], info[site_name]['password']

    return id, password

def read_reservation_info():
    """Read private info"""
    info = readAndSave.read_json('reservation_info.json', 'utf8')

    return info["teacher_num"], info["reserve_time"], info["class_holiday"], info["send_to"]


def send_email_when_error_happens(error, send_to):
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(error)
    msg['subject'] = 'Failed to reserve'
    _id, _password = read_id_pw('gmail')
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
    # driver = phantom
    # chromedirver = r'C:\Python35\selenium\webdriver\chromedriver\chromedriver.exe'
    # os.environ['webdriver.chrome.driver'] = chromedirver
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    #로그 기록
    logger = logging.getLogger('mylogger')
    fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    fileHandler = logging.FileHandler('./error.log')
    fileHandler.setFormatter(fomatter)
    logger.addHandler(fileHandler)
    logger.setLevel(logging.DEBUG)
    logger.info("------class for " + date_time)

    chrome = webdriver.Chrome(r'C:\Python35\selenium\webdriver\chromedriver\chromedriver.exe')
    chrome.implicitly_wait(3)
    driver = chrome

    try:
        # 로그인
        driver.get('https://engoo.co.kr/members/sign_in')  # url
        logger.info("get 완료")
        driver.find_element_by_name('member[email]').send_keys(id)
        logger.info("id 완료")
        driver.find_element_by_name('member[password]').send_keys(password)
        driver.find_element_by_xpath('//*[@id="new_member"]/div[3]/div[4]/button').click() #xpath

        #이미 예약했는지 확인
        driver.get('https://engoo.co.kr/dashboard')
        available_reserve_num = driver.find_element_by_class_name('lesson-badge-remaining').text
        if int(available_reserve_num) == 0: # if you already reserved.
            write_reserve_date(date_time)
            print('You already reserved')
            return

        #예약될때까지 선생님 반복
        for teacher_num in teacher_nums:
            driver.get('https://engoo.co.kr/teachers/'+ teacher_num)
            class_time_button = driver.find_element_by_id(date_time)
            class_time_button = class_time_button.find_element_by_tag_name('a')
            time.sleep(1)
            # class_time_button.click()하면 위에 어떤 창이 싸여있으면 안됨
            driver.execute_script("arguments[0].click();", class_time_button)
            time.sleep(3) # To turn on the modal, You need to have a time sleep

            try:
                driver.find_element_by_id('reserve_student_wish').send_keys('hello') # When I don't write it, unknown error happens
                #driver.find_element_by_xpath('//*[@id="ticket_btn"]').click() # ticket
                driver.find_element_by_xpath('//*[@id="reserve_id"]').click() # normal
                driver.quit()
                logger.info(teacher_num+"예약 성공")
                write_reserve_date(date_time) #write the reserved date when succeed
                return
            except ElementNotVisibleException: # Already have a class.
                try:
                    driver.find_element_by_xpath('//*[@id="notifyDialog"]/div/div/div[3]/button').click() # 이미 예약했을때에 나타나는 창
                    driver.quit()
                    write_reserve_date(date_time)
                    print('You already reserved')
                    return
                except ElementNotVisibleException as e: #수업이 이미 있을 때. -> 다른 선생님을 바꾸기
                    logger.error(teacher_num+"수업 이미 있음")
                    continue
                except Exception as e2: # Other error -> Mail
                    logger.error(teacher_num + e2)
                    if send_to != "":
                        send_email_when_error_happens(e2, send_to)
    except Exception as e3:
        logger.error(e3)

    if send_to != "":
        send_email_when_error_happens('There is no class to reserve. plz check',
                                      send_to)  # 다른 선생님도 다 안되었을때 -> 메일 보내기


def engoo_date_str(reserve_time, class_holiday):
    """retrieve the date when being available to take lessen e.g.'dt_2017-04-07_00-30-00'"""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    weekday_dict = readAndSave.read_json('korean_holiday.json','utf8') # 휴일 data

    def loop_until_workday(calculating_data):
        if weekday_dict[calculating_data.strftime('%Y-%m-%d')]: #휴일이나
            return calculating_data
        else:
            return loop_until_workday(calculating_data + datetime.timedelta(days=1))

    if not class_holiday: #if you don't have class on holiday
        next_day = loop_until_workday(tomorrow)
        date = next_day.strftime('%Y-%m-%d')
 
    else:
        date = tomorrow.strftime('%Y-%m-%d')

    return 'dt_' + date + '_' + reserve_time + '-00'


def write_reserve_date(key):
    reserved_dict = readAndSave.read_json('Did_I_reserved.json', 'utf8')
    reserved_dict[key] = True
    readAndSave.save_json(reserved_dict, 'Did_I_reserved.json', 'utf8')
    return


def already_reserve_tf(key):
    """check whether I reserved or not."""
    reserved_dict = readAndSave.read_json('Did_I_reserved.json', 'utf8')
    return key in reserved_dict


class AutoReserveEngoo:
    def __init__(self, teacher_num, reserve_time, class_holiday, send_to):
        self.id, self.password = read_id_pw('engoo')
        self.teacher_num = teacher_num
        self.reserve_time = reserve_time
        self.send_to = send_to
        self.class_holiday = class_holiday
    def reserve(self):
        date_time = engoo_date_str(self.reserve_time, self.class_holiday)

        if already_reserve_tf(date_time):
            print('You already reserved')
            return
        else:  # If I didn't reserve
            selenium_reserve(self.id, self.password, self.teacher_num, date_time, self.send_to)
    def manual_reserve(self):
        """직접 예약"""
        date_time = engoo_date_str(self.reserve_time, False)
        write_reserve_date(date_time)

if __name__ == "__main__":
    teacher_num, reserve_time, class_holiday, send_to =read_reservation_info()
    me = AutoReserveEngoo(list(teacher_num), reserve_time, class_holiday=="True" , send_to) #if you don't want to send email, plz write None
    me.reserve()
    #me.manual_reserve() # if you already resererve class manually, execute it.

