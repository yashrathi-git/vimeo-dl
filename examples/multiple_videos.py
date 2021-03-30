""" 
Downloading multiple vimeo videos.
"""

from vimeo_downloader import Vimeo

# Replace these with other list of videos you want to download
videos = ['https://vimeo.com/440801455',
		 'https://vimeo.com/504420495',
		 'https://vimeo.com/481277944']

for video in videos:
	v = Vimeo(video)
	stream = v.streams # List of available streams of different quality

	# Selecting and downloading '720p' video
	for s in stream:
		if s.quality == '720p': 
			s.download(download_directory = 'video', filename = v.metadata.title)
			break
	else: # If the loop never break
		print('quality not found')