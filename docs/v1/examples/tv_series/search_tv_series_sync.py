from moviebox_api.v1.core import Search, Session, SubjectType


def search_tv_series():
    client_session = Session()
    search = Search(
        client_session, query="Merlin", subject_type=SubjectType.TV_SERIES
    )

    search_results = search.get_content_sync()

    print(type(search_results))  # (1)

    modelled_search_results = search.get_content_model_sync()

    print(type(modelled_search_results))  # (2)


if __name__ == "__main__":
    search_tv_series()
