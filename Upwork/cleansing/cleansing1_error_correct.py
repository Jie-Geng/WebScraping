#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from pymongo import MongoClient
from scrap.MyDriver import FirefoxDriver


# initializing mongodb client
client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

firefox = FirefoxDriver()


def do_profile(freelancer_row):
    """
    Analyze a freelancer's profile page and get information.
    :param freelancer_row: freelancers's profile_url to be processed.
    :return:
    """

    # open a freelancer's profile page
    url = "https://www.upwork.com" + freelancer_row['profile_id'] + "/"

    profile_soup = firefox.get_page_content(url, random.randint(7, 15))

    # get locality
    try:
        val = profile_soup.find_all("span", attrs={"itemprop": "locality"})
        freelancer_row["City"] = val[0].text
    except IndexError:
        freelancer_row["City"] = ""

    # get country
    try:
        val = profile_soup.find_all("span", attrs={"itemprop": "country-name"})
        freelancer_row["Country"] = val[0].text
    except IndexError:
        freelancer_row["Country"] = ""

    # get title
    try:
        val = profile_soup.find_all("span", attrs={
            "data-ng-bind-html": "vm.cfe.getProfileTitle() | htmlToPlaintext | linkRewrite:'/leaving?ref='"})
        freelancer_row["Title"] = val[0].text
    except IndexError:
        freelancer_row["Title"] = ""

    # get description
    try:
        val = profile_soup.find_all("span", "ng-scope ng-hide")
        freelancer_row["Description"] = val[0].text
    except IndexError:
        freelancer_row["Description"] = ""

    # get job success percentage
    try:
        val = profile_soup.find_all("h3", "m-0-bottom ng-binding")
        freelancer_row["JobRate"] = val[0].text
    except IndexError:
        freelancer_row["JobRate"] = ""

    # get freelancer lever
    val = profile_soup.find(string="Top rated")
    if val is not None:
        freelancer_row["Level"] = "Top rated"
    elif profile_soup.find(string="Rising talent") is not None:
        freelancer_row["Level"] = "Rising talent"
    else:
        freelancer_row["Level"] = "Normal"

    # get Hourly rate
    try:
        val = profile_soup.find_all("cfe-profile-rate")
        val = val[0].find_all("span", attrs={"itemprop": "pricerange"})
        freelancer_row["HourRate"] = val[0].text.strip("\n ")
    except IndexError:
        freelancer_row["HourRate"] = ""

    # get total earned
    try:
        val = profile_soup.find_all("li", attrs={"eo-tooltip": "Amount earned in the past 6 months."})
        val = val[0].find("span")
        freelancer_row["TotalEarned"] = val.text.strip("\n ")
    except IndexError:
        freelancer_row["TotalEarned"] = ""

    # get skills
    skill = ""
    val = profile_soup.find_all("a", attrs={"eo-popover": "skillSearchPromptTooltip.html"})
    for s in val:
        skill = skill + s.text.strip("\n ") + ","

    # insert freelancer's profile into mongodb
    freelancer_row["Skills"] = skill
    print(freelancer_row)

    write_to_mongo(freelancer_row)


def write_to_mongo(update_row):
    """
    This function writes a row - a document for a freelancer - into a mongodb.
    The reason why we use mongodb here is that the skills of freelancers are variable list and I think
    nested document feature of mongodb is useful here.
    And there is another intention to use mongodb in real practise.
    :return:
    """
    pid = update_row['profile_id']
    del update_row['_id']
    collection.update_one({"profile_id": pid}, {"$set": update_row}, True)


# get error rows from db
errorRows = collection.find({'TotalEarned': ''})
for row in errorRows:
    print(row)
    do_profile(row)

firefox.close()
