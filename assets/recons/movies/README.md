# Reconnaisance

This folder stores data discovered during reconnaisance phase.

# Important

subjectType : 1 = Movie
subjectType: 2 = Series

## Everyone's searching

url : https://moviebox.ng/wefeed-h5-bff/web/subject/everyone-search

headers : X-Client-Info	{"timezone":"Africa/Nairobi"}
resonse :

```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "everyoneSearch": [
            {
                "title": "The Vampire Diaries"
            },
            {
                "title": "Teen Wolf"
            },
            {
                "title": "Game of Thrones"
            },
            {
                "title": "Lucifer"
            },
            {
                "title": "Arrow"
            },
            {
                "title": "All American"
            },
            {
                "title": "Squid Game"
            }
        ]
    }
}
```

## Home

url : https://moviebox.ng/wefeed-h5-bff/web/home

COOKIES :

```
account	4127635014202933448|0|H5|1752399419|
i18n_lang	en
```
response : [home.json](home.json)

## Assign Cookies

url : https://moviebox.ng/wefeed-h5-bff/app/get-latest-app-pkgs?app_name=moviebox

response: [assign-cookies](assign-cookies.json)

## Trending 

url : https://moviebox.ng/wefeed-h5-bff/web/subject/trending?uid=5591179548772780352&page=0&perPage=18
response : [trending](trending.json)

url *(without uid)*:  https://moviebox.ng/wefeed-h5-bff/web/subject/trending\?\&page\=0\&perPage\=18

response : [trendinbg-without-uid](trending-without-uid.json)

## Search suggestion

```sh
curl -X POST https://moviebox.ng/wefeed-h5-bff/web/subject/search-suggest -d '{"keyword":"love","perPage":10}'

```

Response

```json
{
    "code": 0,
    "message": "ok",
    "data": {
        "items": [],
        "keyword": "",
        "ops": ""
    }
}
```

## Search Result

url : https://moviebox.ng/web/searchResult?keyword=titanic&utm_source=

response : [search-result](search-result.html)

content-type: text/html

## Specific movie

### Available on web

url :  https://moviebox.ng/movies/the-basketball-diaries-GpkJMWty103\?id\=2518237873669820192\&scene\&page_from\=search_detail\&type\=%2Fmovie%2Fdetail

response: [specific-movie-found](specific-movie-found.html)


### Not available on web (Geo-restrictions)

url : https://moviebox.ng/movies/titanic-m7a9yt0abq6?id=5390197429792821032&scene&page_from=search_detail&type=%2Fmovie%2Fdetail

response : [specific-movie-not-found](specific-movie-not-found.html)

## Hot Movies/TV

- *Normally available after clicking specific movies*

url : https://moviebox.ng/wefeed-h5-bff/web/subject/search-rank
response : [hot-movies](hot-movies.json)

## Recommended/ For You

url : https://moviebox.ng/wefeed-h5-bff/web/subject/detail-rec?subjectId=2518237873669820192&page=1&perPage=24

response : [for-you](for-you.json)


# Download Movie

url : https://moviebox.ng/wefeed-h5-bff/web/subject/download?subjectId=2518237873669820192&se=0&ep=0

response: [download](download.json)
response will include movie files and subtitles.

> [!NOTE]
> Requires [cookies](cookies.json)

# Download subtitle

url : https://cacdn.hakunaymatata.com/subtitle/7236b889e074d8df23ccdf132372e9d9.srt?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jYWNkbi5oYWt1bmF5bWF0YXRhLmNvbS9zdWJ0aXRsZS8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzUzMDEzOTA1fX19XX0_&Signature=2CeE19p-HGmwgpivFR5fZeH3gC~llQ-4N~G4VI3rVphBvRcvjaEzyqogZjEXv8izKDNQ4n-qHhOwhxp4U-NTmO56iLgR11z7icygZC2PX5~Saf7rmb8BZj5~yqcCLj5f4VyyJeJY7amttrZcqgwxk9kSAv6vuIPM1Eq2ebQLggiVS4k8zOID3w9ITPUEspRltl-P8kI9MNHhwsXiuXy~HGzK2Lx0Fa9Y0XgQcAm2K-nwnOKpLPDm~JpiaFmllSGRTG0s0aD4mbha3smA9yBUKd~13PS02EhIgYAa8A8S0eIInMWqMBIQMtjbvCoLIoR-xcn5vBa1rF~OEf76DrhYsg__&Key-Pair-Id=KMHN1LQ1HEUPL

> [!IMPORTANT]
> Do not include cookies
