#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

# import pandas as pd
# import requests
# from pandas import ExcelWriter
from pymongo import MongoClient

from scrap.MyDriver import FirefoxDriver

# This variable was used to avoid "Access Denied" when using request
# Now, by using selenium, it is not currently used


class UpworkScrapper:
    """
    Class to scrap Upwork freelancers
    """

    def __init__(self):
        # a row data which contains a freelancer's information
        self.current_category = ""
        self.progress = {}
        self.freelancer_row = {}

        # initializing mongodb client
        client = MongoClient()
        db = client.get_database("upwork")
        self.collection = db.freelancers
        self.status_collection = db.status

        # get Firefox window
        self.firefox = FirefoxDriver()

    def begin_scrap(self):
        """
        trigger method for scrapping
        :return: None
        """

        nss_list = [80, 90]
        rate_list = ["0-10", "10-30", "30-60", "60"]

        # I have got the upwork category list by other script
        categories = self.get_categories()

        # upwork limits only 500 pages in freelancer list page
        # so, I try to choose some filters which can keep the page number exceeding over 500
        for category in categories:
            self.current_category = category["name"]
            self.progress["category"] = category["name"]

            for nss in nss_list:
                self.progress["nss"] = nss
                for rate in rate_list:
                    self.progress["rate"] = rate
                    url = "https://www.upwork.com" + category["href"] + "nss/" + str(nss) + \
                          "/?revenue=10000&pt=independent&user_pref=1&rate=" + rate
                    self.do_category(url)

    def do_category(self, category_url):
        """
        Process freelancer list pages for the given filter
        :param category_url: detailed url of filter
        :return:
        """

        page_number = 1
        go_on = True

        while go_on:
            self.progress["page_number"] = page_number
            print("Progressing: ", self.progress, end='', flush=True)

            # check if this page has processed already
            if self.status_collection.count_documents(self.progress) > 0:
                print(" Page skipped.")
                page_number = page_number + 1
                continue

            print('')  # new line

            go_on = self.do_page(category_url, page_number)

            # register this page has finished
            if self.progress.get('_id') is not None:
                del self.progress['_id']
            self.status_collection.update_one(self.progress, {'$set': self.progress}, upsert=True)

            page_number = page_number + 1

    def do_page(self, category_url, page_number):
        """
        scrap the freelancer list from the page
        :param category_url: filter url
        :param page_number: page number of freelancer list
        :return:
        """
        page_url = category_url

        # to skip redirecting when page = 1
        if page_number > 1:
            page_url = page_url + "&page=" + str(page_number)

        # open the page
        soup = self.firefox.get_page_content(page_url, random.randint(10, 15))

        # gather freelancer list
        lancers = soup.find_all("article", "row")

        for lancer in lancers:
            name_a = lancer.find_all("a", "freelancer-tile-name")
            lancer_href = name_a[0]["href"].strip()
            lancer_name = name_a[0].text.strip()

            self.freelancer_row.clear()

            # add category and name
            self.freelancer_row["Category"] = self.current_category
            self.freelancer_row["Name"] = lancer_name

            # gather every freelancer's information
            self.do_profile(lancer_href)

        # if the next button is disabled, when we got to the final page
        # Then return False, so that we can go to another filter
        next_button = soup.find_all("li", "pagination-next disabled")
        if len(next_button) > 0:
            return False

        # if the freelancer count is less than 10, yes, of course, it is the final page
        if len(lancers) < 10:
            return False

        return True

    def check_exist(self, profile_url):
        """
        Check a freelancer has been processed early. As a freelancer's profile_url is unique
        this is simply done by checking if I have the profile_url in the collection.
        :param profile_url: Freelancer's upwork profile url.
        :return: True if exists, False or not
        """
        return self.collection.count_documents({"profile_id": profile_url}) > 0

    def do_profile(self, profile_url):
        """
        Analyze a freelancer's profile page and get information.
        :param profile_url: freelancers's profile_url to be processed.
        :return:
        """

        # Check if I have already processed this profile.
        # A freelancer appears so many times in many categories and someone who has already processed doesn't needed
        # to be processed again. profile_url is really effective for testing the duplication as it is an unique id
        # for a freelancer,
        if self.check_exist(profile_url):
            print("-- skip ", self.freelancer_row["Name"])
            return

        # open a freelancer's profile page
        purl = "https://www.upwork.com" + profile_url + "/"

        profile_soup = self.firefox.get_page_content(purl, random.randint(7, 15))

        # Set profile url into current row
        # print(sel_driver.page_source)
        self.freelancer_row["profile_id"] = profile_url

        # get locality
        try:
            val = profile_soup.find_all("span", attrs={"itemprop": "locality"})
            self.freelancer_row["City"] = val[0].text
        except IndexError:
            self.freelancer_row["City"] = ""

        # get country
        try:
            val = profile_soup.find_all("span", attrs={"itemprop": "country-name"})
            self.freelancer_row["Country"] = val[0].text
        except IndexError:
            self.freelancer_row["Country"] = ""

        # get title
        try:
            val = profile_soup.find_all("span", attrs={
                "data-ng-bind-html": "vm.cfe.getProfileTitle() | htmlToPlaintext | linkRewrite:'/leaving?ref='"})
            self.freelancer_row["Title"] = val[0].text
        except IndexError:
            self.freelancer_row["Title"] = ""

        # get description
        try:
            val = profile_soup.find_all("span", "ng-scope ng-hide")
            self.freelancer_row["Description"] = val[0].text
        except IndexError:
            self.freelancer_row["Description"] = ""

        # get job success percentage
        try:
            val = profile_soup.find_all("h3", "m-0-bottom ng-binding")
            self.freelancer_row["JobRate"] = val[0].text
        except IndexError:
            self.freelancer_row["JobRate"] = ""

        # get freelancer lever
        val = profile_soup.find(string="Top rated")
        if val is not None:
            self.freelancer_row["Level"] = "Top rated"
        elif profile_soup.find(string="Rising talent") is not None:
            self.freelancer_row["Level"] = "Rising talent"
        else:
            self.freelancer_row["Level"] = "Normal"

        # get Hourly rate
        try:
            val = profile_soup.find_all("cfe-profile-rate")
            val = val[0].find_all("span", attrs={"itemprop": "pricerange"})
            self.freelancer_row["HourRate"] = val[0].text.strip("\n ")
        except IndexError:
            self.freelancer_row["HourRate"] = ""

        # get total earned
        try:
            val = profile_soup.find_all("li", attrs={"eo-tooltip": "Amount earned in the past 6 months."})
            val = val[0].find("span")
            self.freelancer_row["TotalEarned"] = val.text.strip("\n ")
        except IndexError:
            self.freelancer_row["TotalEarned"] = ""

        # get skills
        skill = ""
        val = profile_soup.find_all("a", attrs={"eo-popover": "skillSearchPromptTooltip.html"})
        for s in val:
            skill = skill + s.text.strip("\n ") + ","

        # insert freelancer's profile into mongodb
        self.freelancer_row["Skills"] = skill
        print(self.freelancer_row)
        self.write_to_mongo()

    @staticmethod
    def get_categories():
        # I have got the upwork category list in earlier stage of this project.
        # This commented code was for it
        #
        #
        # url = "https://www.upwork.com/i/freelancer-categories-all/"
        # page = requests.get(url, headers=headers)
        #
        # # start to analyse contents
        # soup = BeautifulSoup(page.text, 'html.parser')
        #
        # # get the category column
        # categories = soup.find_all(attrs={"tracking-sublocation": "category"})
        # gCategories = []
        # for category in categories:
        #     href = category["href"]
        #     name = category.text
        #
        #     if not name.startswith("All"):
        #         gCategories.append({"name": name, "href": href})
        return [
            {'name': 'Desktop Software Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/desktop-software-development/'},
            {'name': 'Ecommerce Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/ecommerce-development/'},
            {'name': 'Game Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/game-development/'},
            {'name': 'Mobile Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/mobile-development/'},
            {'name': 'Product Management',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/product-management/'},
            {'name': 'QA & Testing', 'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/qa-testing/'},
            {'name': 'Scripts & Utilities',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/scripts-utilities/'},
            {'name': 'Web Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/web-development/'},
            {'name': 'Web & Mobile Design',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/web-mobile-design/'},
            {'name': 'Other - Software Development',
             'href': '/o/profiles/browse/c/web-mobile-software-dev/sc/other-software-development/'},
            {'name': 'Database Administration',
             'href': '/o/profiles/browse/c/it-networking/sc/database-administration/'},
            {'name': 'ERP / CRM Software', 'href': '/o/profiles/browse/c/it-networking/sc/erp-crm-software/'},
            {'name': 'Information Security', 'href': '/o/profiles/browse/c/it-networking/sc/information-security/'},
            {'name': 'Network & System Administration',
             'href': '/o/profiles/browse/c/it-networking/sc/network-system-administration/'},
            {'name': 'Other - IT & Networking',
             'href': '/o/profiles/browse/c/it-networking/sc/other-it-networking/'},
            {'name': 'A/B Testing', 'href': '/o/profiles/browse/c/data-science-analytics/sc/a-b-testing/'},
            {'name': 'Data Visualization',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/data-visualization/'},
            {'name': 'Data Extraction / ETL',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/data-extraction-etl/'},
            {'name': 'Data Mining & Management',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/data-mining-management/'},
            {'name': 'Machine Learning',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/machine-learning/'},
            {'name': 'Quantitative Analysis',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/quantitative-analysis/'},
            {'name': 'Other - Data Science & Analytics',
             'href': '/o/profiles/browse/c/data-science-analytics/sc/other-data-science-analytics/'},
            {'name': '3D Modeling & CAD',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/3d-modeling-cad/'},
            {'name': 'Architecture', 'href': '/o/profiles/browse/c/engineering-architecture/sc/architecture/'},
            {'name': 'Chemical Engineering',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/chemical-engineering/'},
            {'name': 'Civil & Structural Engineering',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/civil-structural-engineering/'},
            {'name': 'Contract Manufacturing',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/contract-manufacturing/'},
            {'name': 'Electrical Engineering',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/electrical-engineering/'},
            {'name': 'Interior Design',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/interior-design/'},
            {'name': 'Mechanical Engineering',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/mechanical-engineering/'},
            {'name': 'Product Design', 'href': '/o/profiles/browse/c/engineering-architecture/sc/product-design/'},
            {'name': 'Other - Engineering & Architecture',
             'href': '/o/profiles/browse/c/engineering-architecture/sc/other-engineering-architecture/'},
            {'name': 'Animation', 'href': '/o/profiles/browse/c/design-creative/sc/animation/'},
            {'name': 'Audio Production', 'href': '/o/profiles/browse/c/design-creative/sc/audio-production/'},
            {'name': 'Graphic Design', 'href': '/o/profiles/browse/c/design-creative/sc/graphic-design/'},
            {'name': 'Illustration', 'href': '/o/profiles/browse/c/design-creative/sc/illustration/'},
            {'name': 'Logo Design & Branding',
             'href': '/o/profiles/browse/c/design-creative/sc/logo-design-branding/'},
            {'name': 'Photography', 'href': '/o/profiles/browse/c/design-creative/sc/photography/'},
            {'name': 'Presentations', 'href': '/o/profiles/browse/c/design-creative/sc/presentations/'},
            {'name': 'Video Production', 'href': '/o/profiles/browse/c/design-creative/sc/video-production/'},
            {'name': 'Voice Talent', 'href': '/o/profiles/browse/c/design-creative/sc/voice-talent/'},
            {'name': 'Other - Design & Creative',
             'href': '/o/profiles/browse/c/design-creative/sc/other-design-creative/'},
            {'name': 'Academic Writing & Research',
             'href': '/o/profiles/browse/c/writing/sc/academic-writing-research/'},
            {'name': 'Article & Blog Writing', 'href': '/o/profiles/browse/c/writing/sc/article-blog-writing/'},
            {'name': 'Copywriting', 'href': '/o/profiles/browse/c/writing/sc/copywriting/'},
            {'name': 'Creative Writing', 'href': '/o/profiles/browse/c/writing/sc/creative-writing/'},
            {'name': 'Editing & Proofreading', 'href': '/o/profiles/browse/c/writing/sc/editing-proofreading/'},
            {'name': 'Grant Writing', 'href': '/o/profiles/browse/c/writing/sc/grant-writing/'},
            {'name': 'Resumes & Cover Letters', 'href': '/o/profiles/browse/c/writing/sc/resumes-cover-letters/'},
            {'name': 'Technical Writing', 'href': '/o/profiles/browse/c/writing/sc/technical-writing/'},
            {'name': 'Web Content', 'href': '/o/profiles/browse/c/writing/sc/web-content/'},
            {'name': 'Other - Writing', 'href': '/o/profiles/browse/c/writing/sc/other-writing/'},
            {'name': 'General Translation', 'href': '/o/profiles/browse/c/translation/sc/general-translation/'},
            {'name': 'Legal Translation', 'href': '/o/profiles/browse/c/translation/sc/legal-translation/'},
            {'name': 'Medical Translation', 'href': '/o/profiles/browse/c/translation/sc/medical-translation/'},
            {'name': 'Technical Translation', 'href': '/o/profiles/browse/c/translation/sc/technical-translation/'},
            {'name': 'Contract Law', 'href': '/o/profiles/browse/c/legal/sc/contract-law/'},
            {'name': 'Corporate Law', 'href': '/o/profiles/browse/c/legal/sc/corporate-law/'},
            {'name': 'Criminal Law', 'href': '/o/profiles/browse/c/legal/sc/criminal-law/'},
            {'name': 'Family Law', 'href': '/o/profiles/browse/c/legal/sc/family-law/'},
            {'name': 'Intellectual Property Law',
             'href': '/o/profiles/browse/c/legal/sc/intellectual-property-law/'},
            {'name': 'Paralegal Services', 'href': '/o/profiles/browse/c/legal/sc/paralegal-services/'},
            {'name': 'Other - Legal', 'href': '/o/profiles/browse/c/legal/sc/other-legal/'},
            {'name': 'Data Entry', 'href': '/o/profiles/browse/c/admin-support/sc/data-entry/'},
            {'name': 'Personal / Virtual Assistant',
             'href': '/o/profiles/browse/c/admin-support/sc/personal-virtual-assistant/'},
            {'name': 'Project Management', 'href': '/o/profiles/browse/c/admin-support/sc/project-management/'},
            {'name': 'Transcription', 'href': '/o/profiles/browse/c/admin-support/sc/transcription/'},
            {'name': 'Other - Admin Support', 'href': '/o/profiles/browse/c/admin-support/sc/other-admin-support/'},
            {'name': 'Customer Service', 'href': '/o/profiles/browse/c/customer-service/sc/customer-service/'},
            {'name': 'Technical Support', 'href': '/o/profiles/browse/c/customer-service/sc/technical-support/'},
            {'name': 'Other - Customer Service',
             'href': '/o/profiles/browse/c/customer-service/sc/other-customer-service/'},
            {'name': 'Display Advertising', 'href': '/o/profiles/browse/c/sales-marketing/sc/display-advertising/'},
            {'name': 'Email & Marketing Automation',
             'href': '/o/profiles/browse/c/sales-marketing/sc/email-marketing-automation/'},
            {'name': 'Lead Generation', 'href': '/o/profiles/browse/c/sales-marketing/sc/lead-generation/'},
            {'name': 'Market & Customer Research',
             'href': '/o/profiles/browse/c/sales-marketing/sc/market-customer-research/'},
            {'name': 'Marketing Strategy', 'href': '/o/profiles/browse/c/sales-marketing/sc/marketing-strategy/'},
            {'name': 'Public Relations', 'href': '/o/profiles/browse/c/sales-marketing/sc/public-relations/'},
            {'name': 'SEM - Search Engine Marketing',
             'href': '/o/profiles/browse/c/sales-marketing/sc/sem-search-engine-marketing/'},
            {'name': 'SEO - Search Engine Optimization',
             'href': '/o/profiles/browse/c/sales-marketing/sc/seo-search-engine-optimization/'},
            {'name': 'SMM - Social Media Marketing',
             'href': '/o/profiles/browse/c/sales-marketing/sc/smm-social-media-marketing/'},
            {'name': 'Telemarketing & Telesales',
             'href': '/o/profiles/browse/c/sales-marketing/sc/telemarketing-telesales/'},
            {'name': 'Other - Sales & Marketing',
             'href': '/o/profiles/browse/c/sales-marketing/sc/other-sales-marketing/'},
            {'name': 'Accounting', 'href': '/o/profiles/browse/c/accounting-consulting/sc/accounting/'},
            {'name': 'Financial Planning',
             'href': '/o/profiles/browse/c/accounting-consulting/sc/financial-planning/'},
            {'name': 'Human Resources', 'href': '/o/profiles/browse/c/accounting-consulting/sc/human-resources/'},
            {'name': 'Management Consulting',
             'href': '/o/profiles/browse/c/accounting-consulting/sc/management-consulting/'},
            {'name': 'Other - Accounting & Consulting',
             'href': '/o/profiles/browse/c/accounting-consulting/sc/other-accounting-consulting/'}]

    def write_xlsx(self):
        """
        This function was designed to write all records into an excel file after everything is finished,
        but it is considered not suitable and it is not currently used.
        Scrapping upwork freelancers is rather a long-term job and there could be many unexpected errors during
        scraping all stuff, so it is not capable to wait until all information is aggregated.
        :return: None
        """
        # df = pd.DataFrame(self.all_rows, columns=['Category', 'Name', 'City', 'Country', 'Title', 'Description',
        #                                           'JobRate', 'Level', 'HourlyRate', 'TotalEarned', 'Skills'])
        # writer = ExcelWriter("upwork_freelancers.xlsx")
        # df.to_excel(writer, 'FreeLancers', index=False)
        pass

    def write_to_mongo(self):
        """
        This function writes a row - a document for a freelancer - into a mongodb.
        The reason why we use mongodb here is that the skills of freelancers are variable list and I think
        nested document feature of mongodb is useful here.
        And there is another intention to use mongodb in real practise.
        :return:
        """
        self.collection.insert_one(self.freelancer_row)
