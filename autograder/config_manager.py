from typing import Dict, Type
from .util import ArgList, AutograderError
from .testcases import TestCase, get_allowed_languages
import configparser
from pathlib import Path


DEFAULT_SOURCE_FILE_STEM = "Homework"
ALLOWED_LANGUAGES = get_allowed_languages()
ARGUMENT_LIST_NAMES = {
    ArgList.submission_precompilation: "SUBMISSION_PRECOMPILATION_ARGS",
    ArgList.submission_compilation: "SUBMISSION_COMPILATION_ARGS",
    ArgList.testcase_precompilation: "TESTCASE_PRECOMPILATION_ARGS",
    ArgList.testcase_compilation: "TESTCASE_COMPILATION_ARGS",
}


class GradingConfig:
    def __init__(self, testcases_dir: Path, config: Path, default_config: Path):
        self.testcases_dir = testcases_dir
        self._configure_grading(config, default_config)

    def _configure_grading(self, config_path: Path, default_config_path: Path):
        cfg = self._read_config(config_path, default_config_path)

        self.timeouts = parse_config_list(cfg["TIMEOUT"], float)
        self.generate_results = cfg.getboolean("GENERATE_RESULTS")
        self.anti_cheat = cfg.getboolean("ANTI_CHEAT")

        self.total_points_possible = cfg.getint("TOTAL_POINTS_POSSIBLE")
        self.total_score_to_100_ratio = self.total_points_possible / 100

        language = cfg["PROGRAMMING_LANGUAGE"]
        if language == "AUTO":
            self.testcase_types = self._figure_out_testcase_types()
        else:
            testcase_type = ALLOWED_LANGUAGES[language.lower().strip()]
            self.testcase_types = {testcase_type.source_suffix: testcase_type}

        self.assignment_name = cfg["ASSIGNMENT_NAME"]

        source = cfg["SOURCE_FILE_NAME"]
        if source == "AUTO":
            source = DEFAULT_SOURCE_FILE_STEM
            self.auto_source_file_name_enabled = True
        else:
            self.auto_source_file_name_enabled = False
        self.lower_source_filename = cfg.getboolean("LOWER_SOURCE_FILENAME")
        if self.lower_source_filename:
            source = source.lower()
        self.source_file_name = source

        self.testcase_weights = parse_config_list(cfg["TESTCASE_WEIGHTS"], float)

        # TODO: Name me better. The name is seriously bad
        self.cli_argument_lists = parse_arglists(cfg)

    @staticmethod
    def _read_config(path_to_user_config: Path, path_to_default_config: Path) -> configparser.SectionProxy:
        default_parser = configparser.ConfigParser()
        default_parser.read(path_to_default_config)

        user_parser = configparser.ConfigParser()
        user_parser.read_dict(default_parser)
        user_parser.read(path_to_user_config)

        return user_parser["CONFIG"]

    def _generate_arglists(self, test: Path):
        arglist = {}
        for arglist_index, arglists_per_testcase in self.cli_argument_lists.items():
            if test.name in arglists_per_testcase:
                arglist[arglist_index] = arglists_per_testcase[test.name]
            elif "ALL" in arglists_per_testcase:
                arglist[arglist_index] = arglists_per_testcase["ALL"]
            else:
                arglist[arglist_index] = tuple()
        return arglist

    def _figure_out_testcase_types(self) -> Dict[str, Type[TestCase]]:
        testcase_types = {}
        for testcase in self.testcases_dir.iterdir():
            testcase_type = get_testcase_type_by_suffix(testcase.suffix)
            if testcase_type is not None:
                testcase_types[testcase_type.source_suffix] = testcase_type

        if testcase_types:
            return testcase_types
        else:
            raise AutograderError(f"Couldn't discover a testcase with correct suffix in {self.testcases_dir}")


def parse_config_list(config_line: str, value_type):
    """Reads in a config line in the format: 'file_name:value, file_name:value, ALL:value '
    ALL sets the default value for all other entries
    """
    config_entries = {}
    for config_entry in config_line.split(","):
        if config_entry.strip():
            testcase_name, value = config_entry.strip().split(":")
            config_entries[testcase_name.strip()] = value_type(value)
    return config_entries


def parse_arglists(cfg):
    argument_lists = {n: {} for n in ARGUMENT_LIST_NAMES}
    for arg_list_index, arg_list_name in ARGUMENT_LIST_NAMES.items():
        arg_list = parse_config_list(cfg[arg_list_name], str)
        for testcase_name, args in arg_list.items():
            argument_lists[arg_list_index][testcase_name] = args.strip().split(" ")
    return argument_lists


def get_testcase_type_by_suffix(suffix: str):
    for testcase_type in ALLOWED_LANGUAGES.values():
        if testcase_type.source_suffix == suffix:
            return testcase_type
