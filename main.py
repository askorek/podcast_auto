import requests as r
import re

main_page = r.get("https://pulsembed.eu/p2em/q5JTqWkbV/")
main_html = str(main_page.content)
patt = r'src="\/\/(.+\/)"'
second_page_url = re.search(patt, main_html)[1]
second_page = r.get("https://" + second_page_url)




print("dupa")