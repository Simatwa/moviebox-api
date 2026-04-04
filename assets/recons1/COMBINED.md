# https://h5-api.aoneroom.com/

## Suggest from Text

```http
POST https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/search-suggest
Accept: application/json
Accept-Encoding: gzip, deflate, zstd
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Content-Length: 31
Content-Type: application/json
Host: h5-api.aoneroom.com
Origin: https://videodownloader.site
Referer: https://videodownloader.site/
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0
x-client-info: {"timezone":"Africa/Nairobi"}
x-request-lang: en

{
    "keyword":"into",
    "perPage":30
}
```

## Click search results

```http
POST https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/search
Accept: application/json
Accept-Encoding: gzip, deflate, zstd
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Content-Type: application/json
Referer: https://videodownloader.site/
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0
x-client-info: {"timezone":"Africa/Nairobi"}
x-request-lang: en

{
    "keyword":"The Warriors",
    "page":1,"perPage":30,
    "subjectType":5
}
```

## Specific item details

```http
GET https://h5-api.aoneroom.com/wefeed-h5api-bff/detail?detailPath=warrior-Au4u1Uu2Nf3
Accept: application/json
Accept-Encoding: gzip, deflate, zstd
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Content-Type: application/json
Host: h5-api.aoneroom.com
Origin: https://videodownloader.site
Referer: https://videodownloader.site/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Sec-GPC: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0
x-client-info: {"timezone":"Africa/Nairobi"}
x-request-lang: en
```

## Downloadable media details

```http
GET https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/download?subjectId=2731661859534295832&se=1&ep=1&detailPath=warrior-Au4u1Uu2Nf3
Accept: application/json
Accept-Encoding: gzip, deflate, zstd
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Content-Type: application/json
Host: h5-api.aoneroom.com
Origin: https://videodownloader.site
Referer: https://videodownloader.site/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Sec-GPC: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0
x-client-info: {"timezone":"Africa/Nairobi"}
x-request-lang: en
```