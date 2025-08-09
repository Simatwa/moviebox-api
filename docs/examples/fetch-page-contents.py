from moviebox_api import MovieDetails, Search, Session, SubjectType
from moviebox_api.models import SearchResultsModel


def main():
    session = Session()

    search = Search(session, query="avatar", subject_type=SubjectType.MOVIES)
    search_results: SearchResultsModel = search.get_content_model_sync()

    # movie_details_inst = search.get_item_details(search_results.first_item)
    movie_details_inst = MovieDetails(search_results.first_item, session)

    # contents = series_details_inst.get_html_content_sync()
    contents = (
        movie_details_inst.get_tag_details_extractor_sync().souped_content.prettify()
        # Prettify contents
    )

    with open("avatar.html", "w") as fh:
        fh.write(contents)


if __name__ == "__main__":
    main()
