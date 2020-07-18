import urllib.request
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build


yt_dev_key = 'AIzaSyBCC_W_q8RV950zZwtbVK8S6rK66cn5WHw'

youtube = build('youtube', 'v3', developerKey=yt_dev_key)


def get_channel_videos(channel_id):
    channel_detail = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = channel_detail['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos = []
    next_page_token = None

    while 1:
        video_playlist = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50,
                                                      pageToken=next_page_token).execute()
        videos += video_playlist['items']
        next_page_token = video_playlist.get('nextPageToken')

        if next_page_token is None:
            break

    with open(videos[0]['snippet']['channelTitle'] + '.xml', 'wb') as file:
        data = ET.Element('rss')
        data.set('xmlns:irc', 'http://www.InstantTvChannel.com/help/mrss/')
        data.set('xmlns:media', 'http://search.yahoo.com/mrss/')
        data.set('version', '2.0')

        channel = ET.SubElement(data, 'channel')

        # for video in videos:
        item = ET.SubElement(channel, 'item')

        videoId = videos[0]['snippet']['resourceId']['videoId']
        video_info = youtube.videos().list(part='snippet, contentDetails, statistics, player', id=videoId).execute()
        print(video_info)

        title = ET.SubElement(item, 'irc:title')
        title.text = videos[0]['snippet']['title']

        thumbnail = ET.SubElement(item, "irc:poster")
        thumbnail.text = video_info['items'][0]['snippet']['thumbnails']['maxres']['url']

        url = ET.SubElement(item, 'irc:url')
        a = (video_info['items'][0]['player']['embedHtml'].find('www'))
        b = (video_info['items'][0]['player']['embedHtml'].find(videoId)) + len(videoId)
        url.text = (video_info['items'][0]['player']['embedHtml'][a:b])

        stream_format = ET.SubElement(item, 'irc:streamformat')
        stream_format.text = 'mp4'

        artist = ET.SubElement(item, 'irc:artist')
        artist.text = video_info['items'][0]['snippet']['channelTitle']

        description = ET.SubElement(item, 'irc:description')
        description.text = video_info['items'][0]['snippet']['description']

        categories = ET.SubElement(item, 'irc:categories')
        categories.text = str(video_info['items'][0]['snippet']['tags']).replace('[', '').replace(']', '')

        duration = ET.SubElement(item, 'irc:length')
        duration.text = video_info['items'][0]['contentDetails']['duration'].replace('PT', '').replace('H', ':').replace('S', '').replace('M', ':')

        published_date = ET.SubElement(item, 'irc:releasedate')
        published_date.text = video_info['items'][0]['snippet']['publishedAt']

        hd_branded = ET.SubElement(item, 'irc:hdbranded')
        if video_info['items'][0]['contentDetails']['definition'] == 'hd':
            hd_branded.text = 'true'
        else:
            hd_branded.text = 'false'

        return file.write(ET.tostring(data))


get_channel_videos('UCE-s6H6S6R91rwLkxCma_qg')
