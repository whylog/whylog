import six

from whylog.teacher.constraint_links_base import ConstraintLinksBase
from whylog.teacher.rule_validation_problems import (
    NotUniqueParserNameProblem, ValidationResult, NotSetLogTypeProblem, WrongPrimaryKeyProblem
)
from whylog.teacher.user_intent import UserParserIntent, UserRuleIntent


class TeacherParser(object):
    def __init__(self, line_object, name, primary_key, log_type):
        self.line = line_object
        self.name = name
        self.primary_key = primary_key
        self.log_type = log_type


class Teacher(object):
    """
    Enable teaching new rule. One Teacher per one entering rule.
    :type pattern_assistant: AbstractAssistant
    :type _parsers: dict[int, TeacherParser]
    :type _constraint_base: dict[int, AbstractConstraint]
    :param _constraint_links: Keeps links between constraints and groups.
                              Link between constraint C and group G exists
                              if C describes relation between G and other groups.
    :type _constraint_links: ConstraintLinksBase
    """

    def __init__(self, config, pattern_assistant):
        self.config = config
        self.pattern_assistant = pattern_assistant

        self._parsers = {}
        self._constraint_base = {}
        self._constraint_links = ConstraintLinksBase()
        self.effect_id = None

    def add_line(self, line_id, line_object, effect=False):
        """
        Adds new line to rule.
        If line_id already exists, old line is overwritten by new line
        and all constraints related to old line are removed.
        """
        if line_id in six.iterkeys(self._parsers):
            self.remove_line(line_id)
        if effect:
            self.effect_id = line_id
        self._add_default_parser(line_id, line_object)

    def _get_names_blacklist(self):
        return [parser.name for parser in six.itervalues(self._parsers)]

    def _add_default_parser(self, line_id, line_object):
        self.pattern_assistant.add_line(line_id, line_object)

        default_pattern_match = self.pattern_assistant.get_pattern_match(line_id)
        default_pattern = default_pattern_match.pattern
        default_groups = default_pattern_match.param_groups

        default_name = self.config.propose_parser_name(
            line_object.line_content, default_pattern, self._get_names_blacklist()
        )
        if default_groups:
            default_primary_key = [min(default_groups.keys())]
        else:
            default_primary_key = []
        default_log_type_name = None

        new_teacher_parser = TeacherParser(
            line_object, default_name, default_primary_key, default_log_type_name
        )
        self._parsers[line_id] = new_teacher_parser

    def remove_line(self, line_id):
        """
        Removes line from rule.
        Assumption: line with line_id exists in rule.
        Removes also all constraints related to this line.
        """

        self._remove_constraints_by_line(line_id)
        self.pattern_assistant.remove_line(line_id)
        del self._parsers[line_id]

    def update_pattern(self, line_id, pattern):
        """
        Loads text pattern proposed by user, verifies if it matches line text.
        Removes constraints related with updating line
        TODO: Update related constraints rather than remove.
        """
        self.pattern_assistant.update_by_pattern(line_id, pattern)
        self._remove_constraints_by_line(line_id)

    def guess_patterns(self, line_id):
        """
        Returns list of guessed patterns for a line.
        """
        return self.pattern_assistant.guess_pattern_matches(line_id)

    def choose_guessed_pattern(self, line_id, pattern_id):
        self.pattern_assistant.update_by_guessed_pattern_match(line_id, pattern_id)

    def set_pattern_name(self, line_id, name):
        self._parsers[line_id].name = name

    def set_converter(self, line_id, group_no, converter):
        # Assumption: converter is one of valid converters
        self.pattern_assistant.set_converter(line_id, group_no, converter)

    def set_primary_key(self, line_id, group_numbers):
        # Assumption: group_numbers is list of integers
        self._parsers[line_id].primary_key = group_numbers

    def set_log_type(self, line_id, log_type):
        # Assumption: log_type is accepted by Config
        self._parsers[line_id].log_type = log_type

    def register_constraint(self, constraint_id, constraint):
        """
        Adds new constraint to rule.
        If constraint_id already exists, constraint with this constraint_id
        is overwritten by new constraint
        """
        if constraint_id in six.iterkeys(self._constraint_base):
            self.remove_constraint(constraint_id)

        self._constraint_base[constraint_id] = constraint
        new_constraint_links = [
            (line_id, group_no, constraint_id) for (line_id, group_no) in constraint.groups
        ]
        self._constraint_links.add_links(new_constraint_links)

    def remove_constraint(self, constraint_id):
        """
        Removes constraint from rule.
        Assumption: Constraint already exists in rule.
        """
        self._constraint_links.remove_links_by_constraint(constraint_id)
        del self._constraint_base[constraint_id]

    def _remove_constraints_by_line(self, line_id):
        constraints_to_remove = self._constraint_links.remove_links_by_line(line_id)
        for constraint_id in constraints_to_remove:
            self.remove_constraint(constraint_id)

    def _remove_constraint_by_group(self, line_id, group_number):
        constraints_to_remove = self._constraint_links.remove_links_by_group(line_id, group_number)
        for constraint_id in constraints_to_remove:
            self.remove_constraint(constraint_id)

    def set_causes_relation(self, relation):
        """
        Determines which combinations of causes can cause effect.
        :param relation: kind of sentence made of AND, OR, brackets and cause symbols.
        """
        pass

    def _validate_primary_keys(self):
        errors = []
        for line_id in six.iterkeys(self._parsers):
            primary_key = self._parsers[line_id].primary_key
            pattern_match = self.pattern_assistant.get_pattern_match(line_id)
            group_numbers = pattern_match.param_groups.keys()
            if set(primary_key) - set(group_numbers):
                errors.append(WrongPrimaryKeyProblem(primary_key, group_numbers, line_id))
        return ValidationResult(errors=errors, warnings=[])

    def _validate_pattern_names(self):
        errors = []
        names_blacklist = self._get_names_blacklist()
        for line_id in six.iterkeys(self._parsers):
            parser = self._parsers[line_id]
            blacklist_except_name = set(names_blacklist) - set([parser.name])
            if names_blacklist.count(parser.name) > 1 or \
                    not self.config.is_free_parser_name(parser.name, blacklist_except_name):
                errors.append(NotUniqueParserNameProblem(line_id))
        return ValidationResult(errors=errors, warnings=[])

    def _validate_log_type(self):
        errors = []
        for line_id in six.iterkeys(self._parsers):
            parser = self._parsers[line_id]
            if parser.log_type is None:
                errors.append(NotSetLogTypeProblem(line_id))
        return ValidationResult(errors=errors, warnings=[])

    def validate(self):
        """
        Verifies if Rule is ready to save.
        """

        primary_keys_validation_result = self._validate_primary_keys()
        pattern_names_validation_result = self._validate_pattern_names()
        log_type_validation_result = self._validate_log_type()
        constraints_validation_result = ValidationResult([], [])  # TODO: fix
        pattern_assistant_validation_result = ValidationResult([], [])  # TODO: fix
        return ValidationResult.result_from_results(
            [
                primary_keys_validation_result,
                pattern_names_validation_result,
                log_type_validation_result,
                constraints_validation_result,
                pattern_assistant_validation_result,
            ]
        )  # yapf: disable

    def _prepare_user_parser(self, line_id):
        """
        :type pattern_match: PatternMatch
        """
        pattern_match = self.pattern_assistant.get_pattern_match(line_id)
        teacher_parser = self._parsers[line_id]
        pattern_type = self.pattern_assistant.TYPE
        return UserParserIntent(
            pattern_type, teacher_parser.name, pattern_match.pattern, teacher_parser.log_type,
            teacher_parser.primary_key, pattern_match.param_groups,
            teacher_parser.line.line_content, teacher_parser.line.offset,
            teacher_parser.line.line_source
        )  # yapf: disable

    def get_rule(self):
        """
        Creates rule for Front that will be shown to user
        """
        user_parsers = dict(
            (line_id, self._prepare_user_parser(line_id)) for line_id in six.iterkeys(
                self._parsers
            )
        )
        user_constraints = [
            constraint.convert_to_user_constraint_intent()
            for constraint in six.itervalues(self._constraint_base)
        ]
        return UserRuleIntent(self.effect_id, user_parsers, user_constraints)

    def save(self):
        """
        Verifies text patterns and constraints. If they meet all requirements, saves Rule.
        """
        validation_result = self.validate()
        if not validation_result.errors:
            self.config.add_rule(self.get_rule())
        else:
            return validation_result
