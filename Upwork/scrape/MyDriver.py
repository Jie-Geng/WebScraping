#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver


class FirefoxDriver:
    """
    Class to manage firefox browser window
    """

    def __init__(self):
        self.sel_driver = webdriver.Firefox(executable_path="C:\\geckodriver.exe")

    def relaunch(self, delay):
        """
        Relaunch the Firefox browser
        :param delay: wait time for finish of page load, in seconds
        :return None
        """

        # close the browser window previously opened
        self.sel_driver.quit()

        # wait for a while
        time.sleep(delay)

        # reopen browser window
        self.sel_driver = webdriver.Firefox(executable_path="C:\\geckodriver.exe")

    def get_page_content(self, url, delay):
        """
        Load a web page and return its contents
        :param url : the web page url to load
        :param delay: wait time for full loading of page in seconds
        :return: BeautifulSoup object
        """

        # if browser cannot connect to the server, repeat it infinitely.
        while True:
            try:
                # load the page
                self.sel_driver.get(url)

                # if the page is loaded, wait for delay seconds until loading would finish.
                # this delay is also to avoid being blocked by upwork due to so frequent access
                time.sleep(delay)

                # read and parse the page contents
                soup = BeautifulSoup(self.sel_driver.page_source, 'html.parser')

                # page loading succeeded. escape from the endless iteration
                break
            except (WebDriverException, TimeoutException):
                # error occurred, do it again
                print("(ERROR) Driver could't be load: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                self.relaunch(60)

        # check if the page is ACCESS DENIED
        # get the title of the page
        elements = soup.find_all("title")
        if len(elements) == 0:
            return soup  # if it has no title, it's may be a normal page

        # if the title is UPWORK ACCESS DENIED, I deal with it
        title = elements[0].text
        if 'access denied' in title.lower():
            print("(ERROR) UPWORK DENIED at ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

            self.relaunch(200)  # relaunch after about 3 minutes

            return self.get_page_content(url, delay)

        # if the title is Upwork - Maintenance, let it wait
        if title == 'Upwork - Maintenance':
            print("(ERROR) UPWORK is under the Maintenance - ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(random.randint(200, 400))  # We don't need relaunch browser.
            return self.get_page_content(url, delay)

        return soup

    def close(self):
        self.sel_driver.quit()
