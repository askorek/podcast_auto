import requests as r
from bs4 import BeautifulSoup

main_page = r.get("https://sites.libsyn.com/402971")
main_html = str(main_page.content)

soup = BeautifulSoup(main_html, 'html.parser')
podcasts_links = [el['href'] for el in soup.find_all('a', {"class": "read_more"})]

for href in podcasts_links:
        single_podcast_page = r.get(href)
        single_podcast_html = str(single_podcast_page.content.decode("utf-8"))
        soup_podcast = BeautifulSoup(single_podcast_html, 'html.parser')
        podcast_title = soup_podcast.title.text

        with open('downloaded.txt') as already_downloaded:
            all_downloaded = already_downloaded.readlines()
            if podcast_title in all_downloaded:
                continue





        download_link = soup_podcast.find('meta', {"name": "twitter:player:stream"})['content']
        file = r.get(download_link)

        with open(podcast_title + '.mp3', mode='wb') as new_file:
            new_file.write(file.content)


        print("dupa")