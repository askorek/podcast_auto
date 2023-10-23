import requests as r
from bs4 import BeautifulSoup
import re
import rfeed

def get_podcast_links():
    main_page = r.get("https://sites.libsyn.com/402971")
    main_html = str(main_page.content)

    soup = BeautifulSoup(main_html, 'html.parser')
    podcasts_links = [el['href'] for el in soup.find_all('a', {"class": "read_more"})]

    return podcasts_links


def check_if_already_downloaded_and_download_if_not(podcast_pages_list):
    podcast_pages_list = list(dict.fromkeys(podcast_pages_list)) # remove duplicates, preserve order

    with open('downloaded.txt', 'w+') as already_downloaded:
        all_downloaded = already_downloaded.readlines()

    for podcast_link in podcast_pages_list:
        if podcast_link in all_downloaded:
            continue
        else:
            download_single_podcast(podcast_link)
            with open('downloaded.txt', 'a') as already_downloaded:
                already_downloaded.writelines(podcast_link + '\n')


def download_single_podcast(podcast_page_url):
    single_podcast_page = r.get(podcast_page_url)
    single_podcast_html = str(single_podcast_page.content.decode("utf-8"))
    soup_podcast = BeautifulSoup(single_podcast_html, 'html.parser')

    regex = r'\/([a-zA-Z0-9-]+)$'
    mp3_filename = re.search(regex, podcast_page_url)[1] + '.mp3'
    mp3_link = soup_podcast.find('meta', {"name": "twitter:player:stream"})['content']

    file = r.get(mp3_link)

    with open(mp3_filename, mode='wb') as new_file:
        new_file.write(file.content)


def get_podcast_metadata(podcast_link):
    metadata = dict()
    podcast_page = r.get(podcast_link)
    html = str(podcast_page.content.decode("utf-8"))

    soup = BeautifulSoup(html, 'html.parser')

    regex = r'\/([a-zA-Z0-9-]+)$'
    mp3_filename = re.search(regex, podcast_link)[1] + '.mp3'
    mp3_link = soup.find('meta', {"name": "twitter:player:stream"})['content']
    podcast_title = soup.find('meta', {"itemprop": "name"})['content']
    podcast_description = soup.find('meta', {"itemprop": "description"})['content']
    date_regex = r'\/([0-9]+)_RAPORT'
    date = re.search(date_regex, mp3_link)[1]

    metadata["mp3_filename"] = mp3_filename
    metadata["mp3_link"] = mp3_link
    metadata["podcast_title"] = podcast_title
    metadata["podcast_description"] = podcast_description
    metadata["date"] = date[0:4] + '-' + date[4:6] + '-' + date[6:8]

    return metadata

aa = get_podcast_metadata('https://sites.libsyn.com/402971/izrael-traci-status-ofiary-europa-na-pewno-nie-jest-bezpieczna-po-tym-co-dzieje-si-na-bliskim-wschodzie')
print(aa)

# podcasts_links = get_podcast_links()
# check_if_already_downloaded_and_download_if_not(podcasts_links)


# TODO:
# get podcast metadata (title, description)
# create rss file
# update rss file