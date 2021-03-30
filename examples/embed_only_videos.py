""" 
Downloading private/embed-only vimeo video. 
If the video isn't embed only you don't need to add embedded_on
"""

from vimeo_downloader import Vimeo

# Replace these two variables to different URL to download that video
vimeo_url = 'https://player.vimeo.com/video/498617513'
embedded_on = 'https://atpstar.com/plans-162.html'
# embedded_on is  the URL of site video is embedded on without query parameters.

v = Vimeo(vimeo_url, embedded_on) 

stream = v.streams # List of available streams of different quality
# >> [Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]

# Download best stream
stream[-1].download(download_directory = 'video', filename = 'test_stream')

# Download video of particular quality, example '540p'
for s in stream:
	if s.quality == '540p':
		s.download(download_directory = 'video', filename = 'test_stream')
		break
else: # If loop never breaks
    print("Quality not found")