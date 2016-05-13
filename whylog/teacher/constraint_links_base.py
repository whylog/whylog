from collections import namedtuple

ConstraintLink = namedtuple('ConstraintLink', ['line_id', 'group_no', 'constraint_id'])


class ConstraintLinksBase:
    """
    Container for links between group and constraint

    :param links: list of links between group and constraint
    :type links: list[ConstraintLink]
    """

    def __init__(self, links=None):
        """
        :param links: list of links between group and constraint represented
                      by simple tuple (line_id, group_no, constraint_id)
        :type links: list[(int, int, int)]
        """

        links = links or []
        self.links = []
        self.add_links(links)

    def get_links(self):
        return [(link.line_id, link.group_no, link.constraint_id) for link in self.links]

    def distinct_constraint_ids(self):
        return set([link.constraint_id for link in self.links])

    def add_links(self, links):
        constraint_links = [ConstraintLink(*link) for link in links]
        self.links = list(set(self.links).union(constraint_links))

    def remove_links_by_line(self, line_id):
        return self._remove_links(self._select_by_line(line_id))

    def remove_links_by_group(self, line_id, group_no):
        return self._remove_links(self._select_by_group(line_id, group_no))

    def remove_links_by_constraint(self, constraint_id):
        return self._remove_links(self._select_by_constraint(constraint_id))

    def _select_by_line(self, select_line_id):
        return [link for link in self.links if link.line_id == select_line_id]

    def _select_by_group(self, select_line_id, select_group_no):
        return [
            link
            for link in self.links
            if link.line_id == select_line_id and link.group_no == select_group_no
        ]

    def _select_by_constraint(self, select_constraint_id):
        return [link for link in self.links if link.constraint_id == select_constraint_id]

    def _remove_links(self, links):
        links_set = set(self.links)
        self.links = list(links_set.difference(links))
        removed_constraint_ids = ConstraintLinksBase(links).distinct_constraint_ids()
        return removed_constraint_ids
