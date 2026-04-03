from moviebox_api.v1 import (
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)


async def tv_series_details_using_item_page_url():

    page_url = "/detail/merlin-sMxCiIO6fZ9?id=8382755684005333552"  # (2)
    client_session = Session()

    details_inst = TVSeriesDetails(
        page_url,
        session=client_session,
    )

    series_details = await details_inst.get_content_model()

    print(type(series_details))  # (1)


if __name__ == "__main__":
    tv_series_details_using_item_page_url()
