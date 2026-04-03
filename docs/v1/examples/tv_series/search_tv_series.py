from moviebox_api.v1.core import Search, Session, SubjectType


async def search_tv_series():
    client_session = Session()
    search = Search(
        client_session, query="Merlin", subject_type=SubjectType.TV_SERIES
    )

    search_results = await search.get_content()

    print(type(search_results))  # (1)

    modelled_search_results = await search.get_content_model()

    print(type(modelled_search_results))  # (2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(search_tv_series())
