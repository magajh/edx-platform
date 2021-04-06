# lint-amnesty, pylint: disable=missing-module-docstring
import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import CourseKey

from common.lib.xmodule.xmodule.partitions.enrollment_track_partition_generator import (
    create_enrollment_track_partition_with_course_id
)
from common.lib.xmodule.xmodule.partitions.partitions import (
    ENROLLMENT_TRACK_PARTITION_ID,
    UserPartition,
)
from common.lib.xmodule.xmodule.partitions.partitions_service import get_user_partition_groups

from .base import OutlineProcessor

log = logging.getLogger(__name__)


class EnrollmentTrackPartitionGroupsOutlineProcessor(OutlineProcessor):
    """
    Processor responsible for applying all enrollment track user partition group to the outline.

    Confining the processor to only EnrollmentTrack user partition is a significant limitation.
    Nonetheless, it is a step towards the goal of supporting
    all partition schemes in the future
    """
    def __init__(self, course_key, user, at_time):
        super().__init__(course_key, user, at_time)
        self.user_groups = []

    def load_data(self):
        user_partition = create_enrollment_track_partition_with_course_id(self.course_key)
        self.enrollment_track_groups = get_user_partition_groups(self.course_key, [user_partition], self.user)

    def _should_block_be_removed(self, block):
        """
        The function to test whether the user is part of the group of which,
        the block is restricting the content to.
        """
        groups = block.user_partition_groups.get(ENROLLMENT_TRACK_PARTITION_ID)
        if not groups:
            return False

        for user_group in self.enrollment_track_groups.values():
            # If the user's partition group, say Masters,
            # does not belong to the partition of the block, say [verified],
            # the block should be removed
            if user_group.id not in groups:
                return True
        return False

    def usage_keys_to_remove(self, full_course_outline):
        removed_usage_keys = set()
        for section in full_course_outline.sections:
            remove_all_children = False
            if self._should_block_be_removed(section):
                removed_usage_keys.add(section.usage_key)
                remove_all_children = True
            for seq in section.sequences:
                if remove_all_children or self._should_block_be_removed(seq):
                    removed_usage_keys.add(seq.usage_key)
        return removed_usage_keys
