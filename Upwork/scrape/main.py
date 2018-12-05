#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file scraps all Upwork $10k+ freelancers.
"""

from scrap.UpworkScraper import UpworkScrapper

if __name__ == "__main__":
    scraper = UpworkScrapper()
    scraper.begin_scrap()
