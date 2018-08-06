#!/usr/bin/env python3
import urllib.request
from bs4 import BeautifulSoup
import multiprocessing as mp
import sys
sys.setrecursionlimit(50000)
import sqlite3

db = sqlite3.connect('etfs.db')
c = db.cursor()
pool = mp.Pool(processes=10)
