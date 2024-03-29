import googleapiclient.discovery
from pytube import YouTube
from time import sleep
from re import sub
import subprocess
import asyncio
import telebot
import os

client = telebot.TeleBot(TELEGRAM_TOKEN)
ytoken = YOUTUBE_TOKEN
def_video_id = ''
def_title = ''
dnl_file = ''

def allow_download(time): # ISO 8601
	global allow
	if len(time) < 9:
		time_re = int(sub(r'\D', '', time))
		if time_re<3000:
			allow = True
		else:
			allow = False
	else:
		allow = False

def request(quest):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = ytoken

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        order="relevance",
        q=quest,
        type="video"
    )
    response = request.execute()

    content = youtube.videos().list(
        part="contentDetails",
        id="Ks-_Mh1QhMc"
    )
    contentDetails = content.execute()

    global def_video_id
    global def_title

    def_video_id = response['items'][0]['id']['videoId']
    def_title = sub(r'[/\\|?]|amp;', '',response['items'][0]['snippet']['title'])
    duration = contentDetails['items'][0]['contentDetails']['duration']
    allow_download(duration)
	
def get_title(video_id):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = ytoken

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id,
        maxResults=1
    )
    response = request.execute()

    global def_title

    def_title = sub(r'[/\\|?]|amp;', '', response['items'][0]['snippet']['title'])
    duration = response['items'][0]['contentDetails']['duration']
    allow_download(duration)

def get_id(link):
	if 'list' in link:
		ready_link = re.split(r'&' ,link.replace('https://www.youtube.com/watch?v=', ''))
		return ready_link[0]
	else:
		ready_link = link.replace('https://www.youtube.com/watch?v=', '')
		return ready_link

def download(link, title):
	video = YouTube(link)

	file = video.streams.filter(type = "audio")
	file.first().download(filename='YouTube')

	thisFile = "YouTube.mp4"
	os.rename(thisFile, title + ".mp3")

	global global_title
	global_title = f"{title}.mp3"

async def delete():
	os.remove(global_title)

print('Бот онлайн')

@client.message_handler(commands=['start', 'help', 'info'])
def info(message):
	client.send_message(message.chat.id, "Данный бот помогает легко находить треки и добавлять их в свою библиотеку Телеграм.\nДля того что бы найти трек, нужно написать комманду /find и указать название или ссылку на трек с youtube")

@client.message_handler(commands=['find'])
def get_song(message):
	if message.text == '/find':
		client.send_message(message.chat.id, 'Неверно указан запрос')
	else:
		start_query = message.text.replace('/find ', '')
		if start_query.startswith('http'):
			video_link = start_query

			try:
				get_title(get_id(video_link))
				if allow:
					download(video_link, def_title)

					with open(global_title, 'rb') as dnl_file:
						client.send_audio(message.chat.id, dnl_file)
						dnl_file.close()

					asyncio.run(delete())
				else:
					client.send_message(message.chat.id, 'Длительности аудиофайла превышает 30 минут')
			except:
				client.send_message(message.chat.id, 'Неверно указанна ссылка')

		else:
			request(start_query)

			if allow:
				dl_link = f'https://www.youtube.com/watch?v={def_video_id}'

				download(dl_link, def_title)

				with open(global_title, 'rb') as dnl_file:
					client.send_audio(message.chat.id, dnl_file)
					dnl_file.close()

				asyncio.run(delete())
			else:
				client.send_message(message.chat.id, 'Длительности аудиофайла превышает 30 минут')

client.polling(none_stop=True,timeout=20)
