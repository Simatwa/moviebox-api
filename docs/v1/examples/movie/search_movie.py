from moviebox_api.v1.core import Search, Session, SubjectType


async def search_movie():
    client_session = Session()

    search = Search(
        session=client_session, query="avatar", subject_type=SubjectType.MOVIES
    )

    search_results = await search.get_content()
    print(type(search_results))  # (1)

    modelled_search_results = await search.get_content_model()  # (2)

    print(type(modelled_search_results))  # (3)


if __name__ == "__main__":
    import asyncio

    asyncio.run(search_movie())
