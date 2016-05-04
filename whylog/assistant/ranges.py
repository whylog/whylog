"""
Auxiliary methods on ranges (intervals)
"""

import six


def complementary_ranges(ranges, start_index, end_index):
    """
    Returns complementary ranges from range (start_index, end_index)
    For start_index = 0, end_index = 20 goes as follows:
    ranges -> complementary_ranges
    [(1, 5), (10, 15)] -> [(0, 1), (5, 10), (15, 20)]
    [(1, 5), (2, 5)] -> [(0, 1), (5, 20)]
    [(1, 5), (2, 10)] -> [(0, 1), (10, 20)]
    """
    ranges_union = _ranges_union(ranges)
    complement_ranges = []

    # edge cases
    if not ranges:
        return [(start_index, end_index)]
    first_start, _ = ranges_union[0]
    if start_index < first_start:
        complement_ranges.append((start_index, first_start))
    _, last_end = ranges_union[-1]
    if end_index > last_end:
        complement_ranges.append((last_end, end_index))

    for (_, previous_end), (succeeding_start, _) in six.moves.zip(ranges_union, ranges_union[1:]):
        complement_ranges.append((previous_end, succeeding_start))
    return sorted(complement_ranges)


def _ranges_union(ranges):
    """
    Joins ranges that intersect as follows:
    ranges -> ranges_union
    [(1, 2), (5, 10)] -> [(1, 2), (5, 10)]
    [(1, 7), (5, 15)] -> [(1, 15)]
    [(1, 5), (5, 15)] -> [(1, 15)]
    """
    if not ranges:
        return []
    sorted_ranges = sorted(ranges)
    ranges_union = [sorted_ranges[0]]
    for start, end in sorted_ranges[1:]:
        last_start, last_end = ranges_union[-1]
        if start <= last_end:
            ranges_union[-1] = last_start, max(last_end, end)
        else:
            ranges_union.append((start, end))
    return sorted(ranges_union)
