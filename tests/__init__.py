from moviebox_api.requests import Session
from moviebox_api.core import Search
from moviebox_api.core import SubjectType

keyword = "Titanic"


def init_search(
    session=Session(), keyword=keyword, subject_type=SubjectType.ALL, per_page=4, page=1
) -> Search:
    return Search(
        session=session,
        keyword=keyword,
        subject_type=subject_type,
        per_page=per_page,
        page=page,
    )
