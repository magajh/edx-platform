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

User = get_user_model()
log = logging.getLogger(__name__)


class UserPartitionGroupsProcessor(OutlineProcessor):
    """
    Processor responsible for applying all user partition group to the outline.

    Currently, this processor only exclude based on EnrollmentTrackPartitionScheme.
    This is a significant limitation, but a step towards the goal of supporting
    all partition schemes in the future
    """

    def _should_block_be_removed(self, block):
        for partition_id, groups in block.user_partition_groups:
            if partition_id == ENROLLMENT_TRACK_PARTITION_ID:
                user_partition = create_enrollment_track_partition_with_course_id(self.course_key)
                user_groups = get_user_partition_groups(self.course_key, [user_partition], self.user)
                if not user_groups:
                    # If the user does not belong into any group of the partition,
                    # the block should be removed
                    return True
                for user_group in user_groups:
                    # If the user's partition group, say Masters,
                    # does not belong to the partition of the block, say [verified],
                    # the block should be removed
                    if user_group.id not in groups:
                        return True
        return False

    def usage_keys_to_remove(self, full_course_outline):
        removed_usage_keys = []
        for section in full_course_outline.sections:
            if self._should_block_be_removed(section):
                removed_usage_keys.append(section.usage_key)
            for seq in section.sequences:
                if self._should_block_be_removed(seq):
                    removed_usage_keys.append(seq.usage_key)
        return removed_usage_keys
