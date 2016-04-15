class ConstraintLinksBase:
    """
    Container for links between group and constraint
    """

    def __init__(self, links_list=None):
        """
        :param links_list: list of links between group and constraint
                          one link is a tuple (line_id, group_no, constraint_id)
        :type links_list: list[(int, int, int)]
        """
        self.links = links_list or []
        self.constr_id_position = 2

    def get_links(self):
        return self.links

    def distinct_constraint_ids(self):
        return set(list(zip(*self.links))[self.constr_id_position])

    def insert_links(self, links_list):
        self.links = list(set(self.links + links_list))

    def remove_links_where(self, line_id=None, group_no=None, constr_id=None):
        base_to_remove = self._select(line_id, group_no, constr_id)
        self._remove_base(base_to_remove)

    def _select(self, select_line_id=None, select_group_no=None, select_constr_id=None):
        selected_base = [
            (line_id, group_no, constr_id)
            for (line_id, group_no, constr_id) in self.links
            if (
                (select_line_id is None or line_id == select_line_id) and (
                    select_group_no is None or group_no == select_group_no
                ) and (
                    select_constr_id is None or constr_id == select_constr_id
                )
            )
        ]
        return ConstraintLinksBase(selected_base)

    def _remove_base(self, base_to_remove):
        """
        :type base_to_remove: ConstraintLinksBase
        """
        base_set = set(self.links)
        sub_base_set = set(base_to_remove.links)
        self.links = list(base_set.difference(sub_base_set))
