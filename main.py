import argparse
import getpass
import json
import os.path
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

search = "/html/body//div[@role='main']/table[@class='main-table']//form[@role='search']//button[@role='button']"
timeout = 2


class DefectCheck:

        # with open('cookies.txt', 'w') as cookief:
        #     # save the cookies as json format
        #     cookief.write(json.dumps(driver.get_cookies()))
        # self.driver.close()

    def __init__(self):
        self.driver = None

    def set_up(self):
        chrome_options = Options()
        if not setup:
            chrome_options.add_argument("--headless")
        if setup:
            chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(
            f"--user-data-dir=C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        s = Service(ChromeDriverManager().install())
        chrome_options.add_argument("--profile-directory=Default")
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        if setup:
            self.driver.get("https://www.wykop.pl")
            time.sleep(30)

    def loadExcel(self, file):
        load = pd.read_excel(f"{file}", 'Arkusz3')
        linklist = load["Link"].to_list()
        linklist = list(dict.fromkeys(linklist))
        return linklist

    def checkClosed(self, link_list, new_list=[]):
        for i in link_list:
            self.driver.get(f'https://{i}')
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Yandex']"))
                WebDriverWait(self.driver, timeout).until(element_present)
                self.driver.find_element(By.XPATH, search)
                new_list.append(i)
            except NoSuchElementException:
                print(f"ERROR : No element found on {i}")
                pass
            except TimeoutException:
                print(f"ERROR : Timeout exceeded. Page {i} not loaded correctly.")
                pass
        return new_list

    def listClosed(self, closed_list):
        print(f"\nList of closed defects:\n------------------------------------------------------")
        for i in closed_list:
            print(str(i))

    def teardown(self):
        self.driver.close()

    def getOpt(self, argv):

        def isfile_check(path):
            if not os.path.isfile(f'{path}'):
                raise argparse.ArgumentTypeError("%s does not exist or path is broken." % path)
            return path

        parser = argparse.ArgumentParser \
            (usage="python3 main.py [-h] -i <file_path>",
             description="Description",
             epilog="© 2022, wiktor.kobiela", prog="DefectCheck",
             add_help=False,
             formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=120, width=250))

        required = parser.add_argument_group('required arguments')
        helpful = parser.add_argument_group('helpful arguments')

        required.add_argument('-i', action='store', dest="file", required=True, metavar="<path>",
                              help='Provide path to excel file generated from validationsraports', type=isfile_check)
        helpful.add_argument('-s', action='store_true', dest="setup", help="Login to portal to store credentials",
                             default=False)
        helpful.add_argument('-h', action='help', help='show this help message and exit')

        args = parser.parse_args()
        return args.file, args.setup

    def run(self, input_file):
        self.set_up()
        links = self.loadExcel(input_file)
        closed_list = self.checkClosed(links)
        self.listClosed(closed_list)
        self.teardown()


check = DefectCheck()
file, setup = check.getOpt(sys.argv[1:])
if setup:
    check.set_up()
else:
    check.run(file)
