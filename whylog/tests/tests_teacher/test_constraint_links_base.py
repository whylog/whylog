from unittest import TestCase

from whylog.teacher.constraint_links_base import ConstraintLinksBase


class TestBasic(TestCase):
    def setUp(self):
        self.links = [
            (1, 10, 100),
            (1, 20, 200),
            (2, 10, 100),
            (2, 10, 200),
            (2, 20, 100),
            (2, 20, 200),
        ]

    def test_distinct_constraint_ids(self):
        constraint_links = ConstraintLinksBase(self.links)
        assert set(constraint_links.distinct_constraint_ids()) == set([100, 200])

    def test_insert_links(self):
        constraint_links = ConstraintLinksBase(self.links)
        new_links = [(2, 20, 200), (3, 30, 300)]
        constraint_links.insert_links(new_links)
        constr_links = constraint_links.get_links()
        assert len(self.links) + 1 == len(constr_links)
        assert set(constr_links) == set(
            [
                (1, 10, 100),
                (1, 20, 200),
                (2, 10, 100),
                (2, 10, 200),
                (2, 20, 100),
                (2, 20, 200),
                (3, 30, 300),
            ]
        )

    def test_remove_by_line(self):
        constraint_links = ConstraintLinksBase(self.links)
        constraint_links.remove_links_where(line_id=1)
        assert set(constraint_links.get_links()) == set(
            [
                (2, 10, 100),
                (2, 10, 200),
                (2, 20, 100),
                (2, 20, 200),
            ]
        )

    def test_remove_by_group(self):
        constraint_links = ConstraintLinksBase(self.links)
        constraint_links.remove_links_where(line_id=2, group_no=20)
        assert set(constraint_links.get_links()) == set(
            [
                (1, 10, 100),
                (1, 20, 200),
                (2, 10, 100),
                (2, 10, 200),
            ]
        )
