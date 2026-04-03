from moviebox_api.v1 import (
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)


async def tv_series_details_using_search_results_item():
    client_session = Session()
    search = Search(
        client_session, query="Merlin", subject_type=SubjectType.TV_SERIES
    )

    search_results = await search.get_content_model()

    target_item = search_results.first_item  # (1)

    details_inst = TVSeriesDetails(
        target_item,
        session=client_session,
    )

    series_details = await details_inst.get_content_model()

    print(type(series_details))  # (2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(tv_series_details_using_search_results_item())
