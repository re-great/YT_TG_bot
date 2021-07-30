import telebot
from telebot import types
import time
import os 


from googleapiclient.discovery import build


api_key = os.getenv('YT_API_KEY')
Tele_key = os.getenv('TG_API_KEY')
youtube = build('youtube','v3',developerKey = api_key)
bot = telebot.TeleBot(Tele_key)



def find_start(sample):
	for text in sample:
		if(text[0] == '@'):
			return text

	return "0"




	

############### BACK BUTTON HANDLER AND KEYBOARD INLINE#############################

def mainmenu(cid):
	print('mainmenu')
	markup = types.InlineKeyboardMarkup()
	markup.row_width = 2


	b1_1 = types.InlineKeyboardButton("Playlists" , callback_data = "playlist*#" + str(cid) ) 
	#b1_2 = types.InlineKeyboardButton("Subs count" , callback_data = "SUBS*#" + str(cid))
	b1_3 = types.InlineKeyboardButton("Top videos" , callback_data = "top vids*#" + str(cid))
	b1_4 = types.InlineKeyboardButton("More statistics" , callback_data = 'more*#'+ str(cid))


	markup.add( b1_1, b1_3, b1_4)

	return markup


def playlist_menu(cid):
		
	print(cid , ' in playlist_menu')

	request = youtube.playlists().list(part = 'snippet' , channelId=cid , maxResults = 5).execute()
	print(request)
	pl_ids = []
	pl_titles = []

	keyboard = types.InlineKeyboardMarkup()

	k = min(5 , len(request['items']))
	print(k , " is k ")
	for i in range(0,k):
		
		print(str(request['items'][i]['id']) , " is plid " , i)
		b = types.InlineKeyboardButton(request['items'][i]['snippet']['title'] , callback_data = str(request['items'][i]['id']) + "*#" + str(cid))
		keyboard.add(b)

		
		print(request['items'][i]['snippet']['title'])
	
	back = types.InlineKeyboardButton('<= BACK' , callback_data = 'BACKTOMAIN*#' + str(cid))
	keyboard.add(back)

	keyboard.row_width = 1
	return keyboard
		


def topvids_menu(cid):
	keyboard = types.InlineKeyboardMarkup()

	b1 = types.InlineKeyboardButton('1.Title(working on it)' , callback_data = 'NODE*#' + str(cid))
	b2 = types.InlineKeyboardButton('2.Title(working on it)' , callback_data = 'NODE*#' + str(cid))
	b3 = types.InlineKeyboardButton('3.Title(working on it)' , callback_data = 'NODE*#'+ str(cid))
	b4 = types.InlineKeyboardButton('<= BACK' , callback_data = 'BACKTOMAIN*#'+ str(cid))

	keyboard.row_width = 1
	keyboard.add(b1,b2,b3,b4);

	return keyboard
	


def moremenu(cid):
	keyboard = types.InlineKeyboardMarkup()

	li = [ 'subscriberCount' , 'viewCount' , 'videoCount' ]

	request = youtube.channels().list( part = 'statistics' , id = cid).execute()

	keyboard = types.InlineKeyboardMarkup()

	for key in li:

		#b = types.InlineKeyboardButton(key + " : " + str(request['items'][0]['statistics'][key]) , callback_data = key + "PLID*#" + str(cid))
		b = types.InlineKeyboardButton(key + " : " + str(request['items'][0]['statistics'][key]) , callback_data = 'NODE*#')
		keyboard.add(b)

	keyboard.row_width = 1

	back = types.InlineKeyboardButton('<= BACK' , callback_data = 'BACKTOMAIN*#' + str(cid))
	keyboard.add(back)


	return keyboard



def pl_expanded(pl_id , cid):

	keyboard = types.InlineKeyboardMarkup()

	request = youtube.playlists().list( part = 'snippet, contentDetails , player' , id = pl_id).execute()

	uploaded_on = request['items'][0]['snippet']['publishedAt']
	video_nos  = request['items'][0]['contentDetails']['itemCount']
	html_link = "https://www.youtube.com//playlist?list=" + pl_id
	print(html_link)

	b1 = types.InlineKeyboardButton("uploaded_on : " + str(uploaded_on) , callback_data = "NODE*#")
	b2 = types.InlineKeyboardButton("Total vids in playlist : " + str(video_nos) , callback_data = "NODE*#")
	b3 = types.InlineKeyboardButton( text = "OPEN LINK" , url = html_link )
	back = types.InlineKeyboardButton("<= BACK" , callback_data = "playlist*#" + str(cid))

	keyboard.row_width = 1
	keyboard.add(b1 , b2 , b3 , back)
	return keyboard







##################### COMMANDS ########################################################





@bot.message_handler(commands = ['start','help'])
def send_welcome(message):
	bot.reply_to(message,"""how's it goin B R U H 
		use /ytinfo (videolink) the only available option right now""")





@bot.message_handler(commands = ['ytinfo'])
def ytchannelfromurl(message):


	print('here')
	url = message.text.split(' ' , 1)[1]

	video_id = ""
	video_id = url.split('v=')[-1]
	if(len(video_id) != 11 ):
		video_id = url.split('/')[-1]

	info = youtube.videos().list( id = video_id ,
		part = 'statistics , snippet , topicDetails').execute()

	usable = info['items']

	if(len(info['items']) == 0):
		bot.reply_to(message , "Unrecognised link , send /ytinfo YT VIDEO LINK")

	else:
		cid = str(usable[0]['snippet']['channelId'])
		print("cid : ",cid)
		
		title = usable[0]['snippet']['title']
		channel_name = usable[0]['snippet']['channelTitle']

		print(f"title : {title} \nCHANNEL FOUND SUCCESSFULLY")


		bot.reply_to(message , f"video title: {title} \n\n*CHANNEL FOUND SUCCESSFULLY*" , parse_mode = "Markdown")


		bot.send_message(message.chat.id , f'choose further option for *{channel_name}*' , reply_markup=mainmenu(cid) , parse_mode = "Markdown")

	
######################  CALLBACK QUERIES #################################################

@bot.callback_query_handler(lambda query : "*#" in query.data )
def reply_playlist(query):

	cid = query.data.split('*#')[-1]
	print(cid , " in callback")
	if('playlist' in query.data) :

		
		bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text="Top playlists", reply_markup=playlist_menu(cid))
		bot.answer_callback_query(query.id , text = "done")


	elif ('top vids' in query.data):
		bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text="TOP videos", reply_markup=topvids_menu(cid))
		bot.answer_callback_query(query.id , text = "done")

	elif ("BACKTOMAIN" in query.data):

		print(query.message.chat.id , query.message.message_id , " in back button func\n")
		bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text = 'choose now' , reply_markup=mainmenu(cid))
		bot.answer_callback_query(query.id , text = "done back")

	elif ('more' in query.data):
		bot.edit_message_text(chat_id = query.message.chat.id , message_id=query.message.message_id , text = 'here are S T A T S' , reply_markup = moremenu(cid))
		bot.answer_callback_query(query.id , text = 'done')

	elif ('PL' in query.data):

		pl_id = query.data.split('*#')[0]
		print(pl_id , " finally mf")


		bot.edit_message_text(chat_id = query.message.chat.id , message_id=query.message.message_id , text = 'PLAYLIST Details' , reply_markup = pl_expanded(pl_id , cid))


		bot.answer_callback_query(query.id , text = "abhi itna hi hua hai bhai")


	elif ('NODE*#' in query.data):

		print('in node callback')
		bot.answer_callback_query( query.id , text = "NO further option right now" , show_alert = True)



while True:
	try:
		bot.polling()

	except Exception :
		time.sleep(5)





