"""
Secondary models - for specific item details
after basic search/discovery
"""

from pydantic import BaseModel

from moviebox_api.v1.extractor.models.json import (
    MetadataModel,
    PostListModel,
    ResourceModel,
    StarsModel,
)
from moviebox_api.v2.models.basics import SearchResultsItem


class SpecificItemDetailsModel(BaseModel):
    """For all subjectTypes"""

    subject: SearchResultsItem
    stars: list[StarsModel]
    resource: ResourceModel
    metadata: MetadataModel
    isForbid: bool
    watchTimeLimit: int
    postList: PostListModel
