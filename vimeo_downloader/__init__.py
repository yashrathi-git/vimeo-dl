"""
Downloads Vimeo videos and retrieve metadata such as views, likes, comments, duration.

Features
    * Easy to use and friendly API.
    * Support for downloading private or embed only Vimeo videos.
    * Retrieve direct URL for the video file.
Usage:
    $ from vimeo_downloader import Vimeo
    $ v = Vimeo('https://vimeo.com/503166067')
    $ meta = v.metadata
    $ s = v.streams
    $ s
        [Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]
    $ best_stream = s[-1] # Select the best stream
    $ best_stream.filesize
    '166.589421 MB'
    $ best_stream.direct_url
    'https://vod-progressive.akamaized.net.../2298326263.mp4'
    $ best_stream.download(download_directory='DirectoryName',filename='FileName')
    # For private or embed only videos
    $ v = Vimeo('https://player.vimeo.com/video/498617513',
                  embedded_on='https://atpstar.com/plans-162.html') 
"""
import os
import re
from collections import namedtuple
from typing import List, NamedTuple, Optional
from urllib.parse import parse_qs, urlparse

import requests
from tqdm import tqdm

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
}
config = "https://player.vimeo.com/video/{}/config"
details = "http://vimeo.com/api/v2/video/{}.json"


class URLNotSupported(Exception):
    pass


class RequestError(Exception):
    pass


class UnableToParseHtml(Exception):
    pass


class URLExpired(RequestError):
    pass


class Metadata(NamedTuple):
    """
    These predefined fields are for enchanced editor/IDE autocompletion.
    """

    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    upload_date: Optional[str] = None
    thumbnail_small: Optional[str] = None
    thumbnail_medium: Optional[str] = None
    thumbnail_large: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_url: Optional[str] = None
    user_portrait_small: Optional[str] = None
    user_portrait_medium: Optional[str] = None
    user_portrait_large: Optional[str] = None
    user_portrait_huge: Optional[str] = None
    duration: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    tags: Optional[str] = None
    embed_privacy: Optional[str] = None
    likes: Optional[str] = None
    views: Optional[str] = None
    number_of_comments: Optional[str] = None


class _Stream:
    def __init__(self, direct_url: str, quality: str, title: str):
        self._direct_url = direct_url  # Direct url for the mp4 file
        self._quality = quality  # Quality of the stream
        self.title = title

    def __repr__(self):
        return f"Stream({self._quality})"

    def __lt__(self, other):
        """
        Streams are sortable based on quality
        """
        return int(self._quality[:-1]) < int(other._quality[:-1])

    @property
    def direct_url(self):
        return self._direct_url

    @property
    def quality(self):
        return self._quality

    def download(
        self, download_directory: str = "", filename: str = None, mute: bool = False
    ):
        """
        Downloads the video with progress bar if `mute=False`
        """

        if (filename is None) and (self.title is None):
            try:
                filename = re.findall(r"\/(\d+\.mp4|webm$)", self._direct_url)[0]
            except IndexError:
                filename = f"{self._quality}.mp4"
        elif (filename is None) and self.title:
            filename = self.title
            if not self.title.endswith(".mp4"):
                filename += ".mp4"
        else:
            if not filename.endswith(".mp4"):
                filename += ".mp4"
        r = requests.get(self._direct_url, stream=True, headers=headers)
        if not r.ok:
            if r.status_code == 410:
                raise URLExpired("The download URL has expired.")
            raise RequestError(f"{r.status_code}: Unable to fetch the video.")
        dp = os.path.join(download_directory, filename)
        if download_directory:
            if not os.path.isdir(download_directory):
                os.makedirs(download_directory)
        with open(dp, "wb") as f:
            total_length = int(r.headers.get("content-length"))
            chunk_size = 1024
            if not mute:
                for chunk in tqdm(
                    iterable=r.iter_content(chunk_size=chunk_size),
                    total=total_length // chunk_size,
                    unit="KB",
                    desc=filename,
                ):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            else:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        return dp  # it is essential for file response.

    @property
    def filesize(self) -> str:
        """
        Returns str with filesize in MB.
        """

        r = requests.get(self._direct_url, stream=True, headers=headers)
        return str(int(r.headers.get("content-length")) / 10**6) + " MB"


class Vimeo:
    """
    Fetch meta data and download video streams.
    """

    def __init__(
        self,
        url: str,
        embedded_on: Optional[str] = None,
        cookies: Optional[str] = None,
    ):
        self._url = (
            urlparse(url)._replace(query=None).geturl()
        )  # URL for the vimeo video
        self._video_id = self._validate_url()  # Video ID at the end of the link
        self._headers = headers
        self._cookies = dict(cookies_are=cookies)
        self._params = self._extract_query(url)
        if embedded_on:
            self._headers["Referer"] = embedded_on

    def _extract_query(self, original_url):
        return parse_qs(qs=urlparse(original_url).query)

    def _validate_url(self):
        """
        This validates if the URL is of Vimeo and returns the video ID
        """

        # Remember, the regexes are matched in order

        accepted_pattern = [
            r"^https:\/\/player.vimeo.com\/video\/(\d+)$",
            r"^https:\/\/vimeo.com\/(\d+)$",
            r"^https://vimeo.com/groups/.+?/videos/(\d+)$",
            r"^https://vimeo.com/manage/videos/(\d+)$",
            r"^https://vimeo.com/(\d+)/[a-zA-Z0-9]+$",
            r"^https://vimeo.com/channels/staffpicks/(\d+)$",
        ]
        for pattern in accepted_pattern:
            match = re.findall(pattern, self._url)
            if match:
                return match[0]
        # If none of the patterns is matched exception is raised
        raise URLNotSupported(f"{self._url} is not supported")

    def _extractor(self) -> dict:
        """
        Extracts the direct mp4 link for the vimeo video
        """
        if self._cookies.get("cookies_are") is not None:
            js_url = requests.get(
                config.format(self._video_id),
                headers=self._headers,
                cookies=self._cookies,
                params=self._params,
            )
        else:
            js_url = requests.get(
                config.format(self._video_id),
                headers=self._headers,
                params=self._params,
            )

        if not js_url.ok:
            if js_url.status_code == 403:
                # If the response is forbidden it tries another way to fetch link
                try:
                    html = requests.get(
                        self._url, headers=self._headers, params=self._params
                    )
                except AttributeError:
                    raise RequestError(
                        "403: If the video is embed only, also provide the embed URL "
                        "on which it is embedded, Vimeo(url=<vimeo_url>,embedded_on=<url>)"
                    )
                if html.ok:
                    try:
                        url = config.format(self._video_id).replace("/", r"\\/")
                        pattern = '"({}.+?)"'.format(url)

                        request_conf_link = re.findall(pattern, html.text)[0].replace(
                            r"\/", "/"
                        )

                        js_url = requests.get(request_conf_link, headers=self._headers)
                        return js_url.json()
                    except IndexError:
                        raise UnableToParseHtml("Couldn't find config url")

                else:
                    if html.status_code == 403:
                        raise RequestError(
                            (
                                f"{html.status_code}: If the video is embed only, also provide the url "
                                "on which it is embedded, Vimeo(url=<vimeo_url>,embedded_on=<url>)"
                            )
                        )
                    else:
                        raise RequestError(
                            f"{html.status_code}: Unable to retrieve download links"
                        )
            else:
                raise RequestError(
                    f"{js_url.status_code}: Unable to retrieve download links"
                )
        try:
            js_url = js_url.json()
        except Exception as e:
            raise RequestError(f"Couldn't retrieve download links: {e}")
        return js_url

    def _get_meta_data(self):
        """
        Retrieves meta data for the video
        """
        if self._cookies:
            video_info = requests.get(
                details.format(self._video_id),
                headers=self._headers,
                cookies=self._cookies,
            )
        else:
            video_info = requests.get(
                details.format(self._video_id), headers=self._headers
            )
        if not video_info.ok:
            raise RequestError(
                f"{video_info.status_code}: Unable to retrieve meta data."
            )
        try:
            video_info = video_info.json()
        except Exception as e:
            raise RequestError(f"Couldn't retrieve meta data: {e}")
        return video_info

    @property
    def metadata(self) -> Metadata:
        """
        Fetch metadata and return it in form of namedtuple.
        """

        self._meta_data = self._get_meta_data()[0]
        if "stats_number_of_likes" in self._meta_data.keys():
            self._meta_data["likes"] = self._meta_data.pop("stats_number_of_likes")
        if "stats_number_of_plays" in self._meta_data.keys():
            self._meta_data["views"] = self._meta_data.pop("stats_number_of_plays")
        if "stats_number_of_comments" in self._meta_data.keys():
            self._meta_data["number_of_comments"] = self._meta_data.pop(
                "stats_number_of_comments"
            )

        # If the Vimeo API returns with some unexpected fields, in some cases
        # a regular namedtuple will be returned
        try:
            metadata = Metadata(**self._meta_data)
            return metadata
        except TypeError:
            metadata = namedtuple("Metadata", self._meta_data.keys())
        return metadata(**self._meta_data)

    @property
    def streams(self) -> List[_Stream]:
        """
        Get all available streams for a video
        """

        js_url = self._extractor()
        try:
            title = js_url["video"]["title"]
        except KeyError:
            title = None
        dl = []
        for stream in js_url["request"]["files"]["progressive"]:
            url = stream["url"]
            if not requests.get(url, stream=True).ok:
                continue
            stream_object = _Stream(
                quality=stream["quality"], direct_url=url, title=title
            )
            dl.append(stream_object)
        dl.sort()
        return dl

    @classmethod
    def from_video_id(
        cls,
        video_id: str,
        embedded_on: Optional[str] = None,
        cookies: Optional[str] = None,
    ):
        self = cls.__new__(cls)
        self._video_id = video_id
        self._headers = headers
        self._cookies = dict(cookies_are=cookies)
        self._params = {}
        if embedded_on:
            self._headers["Referer"] = embedded_on
        return self

    @property
    def best_stream(self) -> _Stream:
        return self.streams[-1]

    def __repr__(self):
        try:
            repr_form = f"Vimeo<{self._url}>"
        except AttributeError:
            repr_form = f"Vimeo<{self._video_id}>"
        return repr_form
