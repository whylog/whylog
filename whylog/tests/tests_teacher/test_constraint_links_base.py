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
        self.constraint_links = ConstraintLinksBase(self.links)

    def test_distinct_constraint_ids(self):
        assert set(self.constraint_links.distinct_constraint_ids()) == set([100, 200])

    def test_add_links(self):
        new_links = [(2, 20, 200), (3, 30, 300)]
        self.constraint_links.add_links(new_links)
        constr_links = self.constraint_links.get_links()
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
        self.constraint_links.remove_links_by_line(1)
        assert set(self.constraint_links.get_links()) == set(
            [
                (2, 10, 100),
                (2, 10, 200),
                (2, 20, 100),
                (2, 20, 200),
            ]
        )

    def test_remove_by_group(self):
        self.constraint_links.remove_links_by_group(2, 20)
        assert set(self.constraint_links.get_links()) == set(
            [
                (1, 10, 100),
                (1, 20, 200),
                (2, 10, 100),
                (2, 10, 200),
            ]
        )

    def test_remove_by_constraint(self):
        self.constraint_links.remove_links_by_constraint(100)
        assert set(self.constraint_links.get_links()) == set(
            [
                (1, 20, 200),
                (2, 10, 200),
                (2, 20, 200),
            ]
        )
