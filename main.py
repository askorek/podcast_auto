import os

import requests as r
from bs4 import BeautifulSoup
import re
import rfeed

MAIN_PAGE = "https://sites.libsyn.com/402971"
DOWNLOADED_FILE = 'downloaded.txt'
RSS_FILENAME = 'podcast.rss'
RSS_TITLE = 'Raport Międzynarodowy'
MY_PAGE_ADRESS = 'frog01.mikr.us:20638'


def check_if_there_are_updates(url, downloaded_txt_file):
    podcasts_links = get_podcasts_links(url)

    with open(downloaded_txt_file, 'r') as already_downloaded:
        all_downloaded = already_downloaded.read().splitlines()

    for podcast_link in podcasts_links:
        if podcast_link in all_downloaded:
            continue
        else:
            return True
    return False


# !!!!!
def check_if_already_downloaded_and_download_if_not(podcast_link, downloaded_file):
    print("checking if " + podcast_link + " needs to be downloaded")
    with open(downloaded_file, 'r') as already_downloaded:
        all_downloaded = already_downloaded.read().splitlines()

    if podcast_link in all_downloaded:
        return
    else:
        print("downloading file from link: " + podcast_link)
        download_single_podcast(podcast_link)
        with open(downloaded_file, 'a') as already_downloaded:
            already_downloaded.write(podcast_link + '\n')


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

    metadata["podcast_link"] = podcast_link
    metadata["mp3_filename"] = mp3_filename
    metadata["mp3_link"] = mp3_link
    metadata["podcast_title"] = podcast_title
    metadata["podcast_description"] = podcast_description
    metadata["date"] = date[0:4] + '-' + date[4:6] + '-' + date[6:8]

    return metadata


def get_all_podcasts_metadata(url):
    podcasts_links = get_podcasts_links(url)

    all_metadata = list()
    for link in podcasts_links:
        metadata = get_podcast_metadata(link)
        all_metadata.append(metadata)

    return all_metadata


def get_podcasts_links(url):
    main_page = r.get(url)
    main_html = str(main_page.content.decode("utf-8"))
    soup = BeautifulSoup(main_html, 'html.parser')
    podcasts_links = [el['href'] for el in soup.find_all('a', {"class": "read_more"})]
    podcasts_links = list(dict.fromkeys(podcasts_links))  # remove duplicates, preserve order
    return podcasts_links


def create_rss_file(all_metadata, rss_filename, my_page_adress, title='Raport międzynarodowy'):
    _items = list()
    for metadata in all_metadata:
        item = rfeed.Item(
            title=metadata['podcast_title'],
            link=metadata['podcast_link'],
            description=metadata['podcast_description'],
            guid=rfeed.Guid(metadata['podcast_link']),
            enclosure=rfeed.Enclosure(url=
                                      my_page_adress + '/' + metadata['mp3_filename'],
                                      length=0,
                                      type='audio/mpeg')
        )
        _items.append(item)

    feed = rfeed.Feed(title=title, items=_items, link=my_page_adress + rss_filename,
                      description='Raport międzynarodowy')

    with open(rss_filename, 'w', encoding="utf-8") as file:
        file.write(feed.rss())


def main():

    # check if downloaded.txt exists, if not create
    if not os.path.exists(DOWNLOADED_FILE):
        open(DOWNLOADED_FILE, 'w').close()

    if not check_if_there_are_updates(MAIN_PAGE, DOWNLOADED_FILE):
        print('Nothing to download')
        return 0

    all_metadata = get_all_podcasts_metadata(MAIN_PAGE)
    print('New data, starting downloading')

    # download missing files
    for metadata in all_metadata:
        link = metadata['podcast_link']
        check_if_already_downloaded_and_download_if_not(link, DOWNLOADED_FILE)

    print("Download finished, creating new RSS file")
    create_rss_file(all_metadata, RSS_FILENAME, MY_PAGE_ADRESS, RSS_TITLE)

    print("All tasks done, finishing")

main()

