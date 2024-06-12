import requests
from bs4 import BeautifulSoup
from datetime import datetime
from phi.tools.newspaper4k import Newspaper4k
import time
import json

articles_json: dict[str:str] = {}
list_of_articles: list[dict[str:str]] = []

