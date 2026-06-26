import logging

import moviebox_api.v1.logger

moviebox_api.v1.logger.logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
