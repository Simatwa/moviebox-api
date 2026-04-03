from moviebox_api.v1 import (
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)


def tv_series_details_using_search_results_item():
    client_session = Session()
    search = Search(
        client_session, query="Merlin", subject_type=SubjectType.TV_SERIES
    )

    search_results = search.get_content_model_sync()

    target_item = search_results.first_item  # (1)

    details_inst = TVSeriesDetails(
        target_item,
        session=client_session,
    )

    series_details = details_inst.get_content_model_sync()

    print(type(series_details))  # (2)


if __name__ == "__main__":
    tv_series_details_using_search_results_item()
