# Vimeo Downloader  <!-- omit in toc -->

[![PyPI](https://img.shields.io/pypi/v/vimeo_downloader?color=blue)](https://pypi.org/project/vimeo-downloader/)
![PyPI - License](https://img.shields.io/pypi/l/vimeo_downloader?color=blue)

Downloads Vimeo videos and retrieve metadata such as views, likes, comments, duration of the video.

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
    - [Metadata](#metadata)
    - [Download video](#download-video)
    - [Download embed only videos](#downloading-embed-only-videos)
    - [Downloading videos that require login](#downloading-videos-that-require-login)
    - [Download with video ID](#download-video-with-video-id)
* [Examples](#examples)

# Features

* Easy to use and friendly API.
* Support for downloading private or embed only Vimeo videos.
* Retrieve direct(.mp4 file) URL for the video.
* Uses type-hints for better editor autocompletion
* Retrieve metadata such as views, likes, comments, duration of the video
* Tested for python 3.6 and above

# Installation

```bash
pip install vimeo_downloader
```

or download the latest version:

```bash
pip install git+https://github.com/yashrathi-git/vimeo_downloader
```

# Usage

```python
>> from vimeo_downloader import Vimeo
>> v = Vimeo('https://vimeo.com/503166067')
```

## Metadata

```python
>> meta = v.metadata
>> meta.title
"We Don't Have To Know - Keli Holiday"
>> meta.likes
214
>> meta.views
8039
>> meta._fields  # List of all meta data fields
('id', 'title', 'description'...)  # Truncated for readability
```

## Download video

```python
>> s = v.streams
>> s
[Stream(240p), Stream(360
p), Stream(540
p), Stream(720
p), Stream(1080
p)]
>> best_stream = s[-1]  # Select the best stream
>> best_stream.filesize
'166.589421 MB'
>> best_stream.direct_url
'https://vod-progressive.akamaized.net.../2298326263.mp4'
>> best_stream.download(download_directory='DirectoryName',
                        filename='FileName')
# Download video with progress bar and other information,
# to disable this behaviour use mute=True
```

## Downloading embed only videos

```python
>> from vimeo_downloader import Vimeo
>> v = Vimeo('https://player.vimeo.com/video/498617513',
             embedded_on='https://atpstar.com/plans-162.html') 
```

For embed only videos, also provide embedded_on parameter to specify the URL on which video is embedded without query
parameters.

```python
>> v.streams
[Stream(240p), Stream(360
p), Stream(540
p), Stream(720
p), Stream(1080
p)]
>> v.streams[-1].download(download_directory='DirectoryName',
                          filename='FileName')
# Downloads the best stream with progress bar and other information, 
# to disable this behaviour use mute=True
```

## Downloading videos that require login

**It uses cookie to authenticate. You could get cookie like this:**

While logged into your account, go to the video URL. Press Command + Shift + C or Control + Shift + C to get to
developer tools. Go to network tab and reload the page. You would see all requests that were made. Click on the top
one (request made to same URL you're on) and scroll down to "Request Headers", there you would find cookie parameter,
copy its value.

```python
from vimeo_downloader import Vimeo

cookies = """
    cookie
 """.strip()

v = Vimeo(
    url="URL",
    cookies=cookies,
)

best_stream = v.best_stream
mp4_url = best_stream.direct_url

title = best_stream.title

## Download
best_stream.download()
```

## Download video with video ID

(New in 0.3.2)
If the above methods, don't work it, you would most likely be able to download video using its vimeo video ID.

```python
from vimeo_downloader import Vimeo

# url: https://vimeo.com/79761619
# video ID: '79761619'
v = Vimeo.from_video_id(video_id='79761619')
```

# Examples

## 1. Downloading embed only videos

`embedded_on` is the URL of site video is embedded on without query parameters.

```python
from vimeo_downloader import Vimeo

# Replace these two variables to different URL to download that video
vimeo_url = 'https://player.vimeo.com/video/498617513'
embedded_on = 'https://atpstar.com/plans-162.html'
# embedded_on is  the URL of site video is embedded on without query parameters.

v = Vimeo(vimeo_url, embedded_on)

stream = v.streams  # List of available streams of different quality
# >> [Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]

# Download best stream
stream[-1].download(download_directory='video', filename='test_stream')

# Download video of particular quality, example '540p'
for s in stream:
    if s.quality == '540p':
        s.download(download_directory='video', filename='test_stream')
        break
else:  # If loop never breaks
    print("Quality not found")
```

## 2. Downloading a list of videos

```python
from vimeo_downloader import Vimeo

# Replace these with other list of videos you want to download
videos = ['https://vimeo.com/440801455',
          'https://vimeo.com/504420495',
          'https://vimeo.com/481277944']

for video in videos:
    v = Vimeo(video)
    stream = v.streams  # List of available streams of different quality

    # Selecting and downloading '720p' video
    for s in stream:
        if s.quality == '720p':
            s.download(download_directory='video', filename=v.metadata.title)
            break
    else:  # If the loop never break
        print('quality not found')
```

# License

Distributed under the MIT licence. Read `LICENSE` for more information
https://github.com/yashrathi-git/vimeo_downloader/blob/main/LICENCE

