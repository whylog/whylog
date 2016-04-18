class ConstraintLinksBase:
    """
    Container for links between group and constraint
    """

    LINE_ID_POSITION = 0
    GROUP_NUMBER_POSITION = 1
    CONSTRAINT_ID_POSITION = 2

    def __init__(self, links_list=None):
        """
        :param links_list: list of links between group and constraint
                          one link is a tuple (line_id, group_no, constraint_id)
        :type links_list: list[(int, int, int)]
        """
        self.links = links_list or []

    def get_links(self):
        return self.links

    def distinct_constraint_ids(self):
        return set(list(zip(*self.links))[self.CONSTRAINT_ID_POSITION])

    def add_links(self, links):
        self.links = list(set(self.links).union(links))

    def remove_links_by_line(self, line_id):
        self._remove_base(self._select_by_line(line_id))

    def remove_links_by_group(self, line_id, group_no):
        self._remove_base(self._select_by_group(line_id, group_no))

    def remove_links_by_constraint(self, constraint_id):
        self._remove_base(self._select_by_constraint(constraint_id))

    def _select_by_line(self, select_line_id):
        return ConstraintLinksBase(
            [
                (
                    line_id, group_no, constr_id
                ) for (line_id, group_no, constr_id) in self.links if line_id == select_line_id
            ]
        )

    def _select_by_group(self, select_line_id, select_group_no):
        return ConstraintLinksBase(
            [
                (line_id, group_no, constr_id)
                for (
                    line_id, group_no, constr_id
                ) in self.links if line_id == select_line_id and group_no == select_group_no
            ]
        )

    def _select_by_constraint(self, select_constraint_id):
        return ConstraintLinksBase(
            [
                (line_id, group_no, constr_id)
                for (
                    line_id, group_no, constr_id
                ) in self.links if constr_id == select_constraint_id
            ]
        )

    def _remove_base(self, base_to_remove):
        """
        :type base_to_remove: ConstraintLinksBase
        """
        base_set = set(self.links)
        sub_base_set = set(base_to_remove.links)
        self.links = list(base_set.difference(sub_base_set))
