from moviebox_api.v1 import MovieDetails, Search, Session, SubjectType


async def movie_details_using_search_results_item():
    client_session = Session()
    search = Search(
        client_session, query="avatar", subject_type=SubjectType.MOVIES
    )

    search_results = await search.get_content_model()

    target_item = search_results.first_item  # search_results.items[0]

    md = MovieDetails(
        target_item,
        session=client_session,
    )

    details = await md.get_content_model()
    print(type(details))

    # <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>


if __name__ == "__main__":
    import asyncio

    asyncio.run(movie_details_using_search_results_item())
