# Reconnaisance

This folder stores data discovered during reconnaisance phase.


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

