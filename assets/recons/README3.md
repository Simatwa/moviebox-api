## Home

```http
https://h5-api.aoneroom.com/wefeed-h5api-bff/home?host=h5.aoneroom.com
```

> Mas to current homepage implementation (v2)

## Home > Popular Movies

```http
https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content?id=997144265920760504&page=1&perPage=50
```
> genreTopId : 997144265920760504 


## Tab Operating

```http
https://h5-api.aoneroom.com/wefeed-h5api-bff/tab-operating?tabId=ONEROOM_MOVIE&host=h5.aoneroom.com
```

> Maps to current homepage implementation (v2)


## Movie/TV-Show Filter Search

```http
POST https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/filter
Content-type: application/json
X-Client-Info:	{"timezone":"Africa/Nairobi"}

{
    "page":1,
    "perPage":50,
    "channelId":1,
    "genre":"All",
    "country":"United States",
    "year":"All",
    "sort":"ForYou",
    "classify":"All"
}
```

