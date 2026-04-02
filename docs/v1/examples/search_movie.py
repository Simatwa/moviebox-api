from moviebox_api.v1.core import Search, Session, SubjectType


async def search_movie():
    client_session = Session()

    search = Search(
        session=client_session, query="avatar", subject_type=SubjectType.MOVIES
    )

    search_results = await search.get_content()
    print(type(search_results))  # <class 'dict'>

    # items = search_results['items'] # list of individual movies matching the query

    modelled_search_results = await search.get_content_model()  # (2)

    print(
        type(modelled_search_results)
    )  # <class 'moviebox_api.v1.models.SearchResultsModel'>

    # items = search_results.items # (1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(search_movie())
