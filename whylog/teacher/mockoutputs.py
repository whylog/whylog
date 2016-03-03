from whylog.teacher.userintent import UserParserIntent, UserConstraintIntent, UserRuleIntent


def create_sample_rule():
    # Constraint types
    identical_constr = "identical"
    different_constr = "different"
    hetero_constr = "hetero"

    # convertions
    to_date = 0
    to_float = 3
    # default: TO_STRING = 1
    """
    content1 = "2015-12-03 12:08:09 Connection error occurred on alfa36. Host name: 2"
    content2 = "2015-12-03 12:10:10 Data migration from alfa36 to alfa21 failed. Host name: 2"
    content3 = "2015-12-03 12:11:00 Data is missing at alfa21. Loss = 567.02 GB. Host name: 101"
    """

    regex1 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Connection error occurred on (.*). Host name: (.*)$"
    regex2 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data migration from (.*) to (.*) failed. Host name: (.*)$"
    regex3 = "^(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) Data is missing at (.*). Loss = (.*) GB. Host name; (.*)$"

    parser1 = UserParserIntent("hydra", regex1, [1], dict([(1, to_date)]))
    parser2 = UserParserIntent("hydra", regex2, [1], dict([(1, to_date)]))
    parser3 = UserParserIntent("filesystem", regex3, [1], dict([(1, to_date), (3, to_float)]))

    parsers = {0: parser1, 1: parser2, 2: parser3}
    effect_id = 2

    constraint1 = UserConstraintIntent(identical_constr, [(0, 2), (1, 2)])
    constraint2 = UserConstraintIntent(identical_constr, [(1, 3), (2, 2)])
    constraint3 = UserConstraintIntent(different_constr, [(1, 2), (1, 3)])
    constraint4 = UserConstraintIntent(hetero_constr, [(0, 3), (1, 4), (2, 4)], [1])

    constraints = [constraint1, constraint2, constraint3, constraint4]

    return UserRuleIntent(parsers, effect_id, constraints)
