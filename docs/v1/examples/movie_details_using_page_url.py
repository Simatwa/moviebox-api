from moviebox_api.v1 import MovieDetails, Session


async def movie_details_using_page_url():
    page_url = "/detail/avatar-WLDIi21IUBa?id=8906247916759695608"  # (1)

    client_session = Session()

    md = MovieDetails(
        page_url,
        session=client_session,
    )

    details = await md.get_content_model()
    print(type(details))  # (2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(movie_details_using_page_url())
