""" 
Links all other movie submodules 
"""
from moviebox_api.requests import Session
from moviebox_api.utils import assert_instance

class Home:
    """Movie listings on landing page"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/home"

    #def __init__(self)

    # TODO: Implement later


class EveryoneSearches:
    """Movies and series everyone searches"""

    _url =  r"https://moviebox.ng/wefeed-h5-bff/web/subject/everyone-search"

    def __init__(self, session:Session):
        """Constructor for `EveryoneSearches`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        
