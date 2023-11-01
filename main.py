import requests as r
from bs4 import BeautifulSoup
import re
import rfeed
from pprint import pp

MAIN_PAGE = "https://sites.libsyn.com/402971"
DOWNLOADED_FILE = 'downloaded.txt'
RSS_FILENAME = 'podcast.rss'
RSS_TITLE = 'Raport Międzynarodowy'
MY_PAGE_ADRESS = 'frog01.mikr.us:20638'

def check_if_there_are_updates(url, downloaded_txt_file):
    podcasts_links = get_podcasts_links(url)

    with open(downloaded_txt_file, 'w+') as already_downloaded:
        all_downloaded = already_downloaded.readlines()

    for podcast_link in podcasts_links:
        if podcast_link in all_downloaded:
            continue
        else:
            return True
    return False

# !!!!!
def check_if_already_downloaded_and_download_if_not(podcast_link, donwloaded_file):
    with open(donwloaded_file, 'w+') as already_downloaded:
        all_downloaded = already_downloaded.readlines()

    if podcast_link in all_downloaded:
        return
    else:
        download_single_podcast(podcast_link)
        with open(donwloaded_file, 'a') as already_downloaded:
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
            guid=metadata['podcast_link'],
            enclosure=rfeed.Enclosure(url=
                                        my_page_adress + metadata['mp3_filename'],
                                        length=0,
                                        type='audio/mpeg')
        )
        _items.append(item)

    feed = rfeed.Feed(title=title, items=_items)

    with open(rss_filename, 'w') as file:
        file.write(feed)

def main():
    if not check_if_there_are_updates(MAIN_PAGE, DOWNLOADED_FILE, MY_PAGE_ADRESS):
        return 0

    all_metadata = get_all_podcasts_metadata(MAIN_PAGE)

    #download missing files
    for metadata in all_metadata:
        link = metadata['podcast_link']
        check_if_already_downloaded_and_download_if_not(link, DOWNLOADED_FILE)

    create_rss_file(all_metadata, RSS_FILENAME, RSS_TITLE)

    pp(all_metadata)




main()

#aa = get_podcast_metadata('https://sites.libsyn.com/402971/izrael-traci-status-ofiary-europa-na-pewno-nie-jest-bezpieczna-po-tym-co-dzieje-si-na-bliskim-wschodzie')
#print(aa)

# podcasts_links = get_podcast_links()
# check_if_already_downloaded_and_download_if_not(podcasts_links)


# TODO:
# create rss file
# update rss file