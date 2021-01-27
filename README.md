# Vimeo Downloader

Downloads Vimeo videos and retrieve metadata such as views, likes, comments, duration of the video.
* Easy to use and friendly API.
* Support for downloading private or embed only Vimeo videos.
* Retrieve direct URL for the video file.


## Installation

```bash
pip install vimeo_downloader
```

## Usage

```python
>>> from vimeo_downloader import Vimeo
>>> v = Vimeo('https://vimeo.com/503166067')
```
#### Metadata
```python
>>> meta = v.metadata
>>> meta.title
"We Don't Have To Know - Keli Holiday"
>>> meta.likes
214
>>> meta.views
8039
>>> meta._fields # List of all meta data fields
('id', 'title', 'description'...) # Truncated for readability
```
#### Download stream
```python
>>> s = v.streams
>>> s
[Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]
>>> best_stream = s[-1] # Select the best stream
>>> best_stream.filesize
'166.589421 MB'
>>> best_stream.direct_url
'https://vod-progressive.akamaized.net.../2298326263.mp4'
>>> best_stream.download(download_directory='DirectoryName',
                        filename='FileName')
# Download video with progress bar and other information,
# to disable this behaviour use mute=True
```
### Downloading private or embed only videos 
```python
>>> from vimeo_downloader import Vimeo
>>> v = Vimeo('https://player.vimeo.com/video/498617513',
              embedded_on='https://atpstar.com/plans-162.html') 
```
For embed only videos, also provide embedded_on parameter to specify the URL on which video is embedded without query parameters.
```python
>>> v.streams
[Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]
>>> v.streams[-1].download(download_directory='DirectoryName',
                           filename='FileName')
# Downloads the best stream with progress bar and other information, 
# to disable this behaviour use mute=True
```


## License
Distributed under the MIT licence. Read `LICENSE` for more information