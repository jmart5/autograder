import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict


SYSTEM_RESERVED_EXIT_CODES = [
    1, 2, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141,
    142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158,
    159, 160, 161, 162, 163, 164, 165, 255
]
# If you want to extend the grader, you change the upper bound of the range
# of ALL_USED_EXIT_CODES
ALL_USED_EXIT_CODES = [0] + list(range(3, 126)) + list(range(166, 255))

EXIT_CODE_COUNT_FOR_RESULTS = 101
ALLOWED_EXIT_CODE_COUNT = EXIT_CODE_COUNT_FOR_RESULTS + 1  # 1 for CHECK_OUTPUT


class ExitCodeEvent(Enum):
    SYSTEM_ERROR = 0
    RESULT = 1
    CHECK_OUTPUT = 2
    CHEAT_ATTEMPT = 3


@dataclass
class ResultFromExitCode:
    event: ExitCodeEvent
    # To prevent dumb mistakes. If a developer misuses the value,
    # the obvious error will most likely occur.
    value: int = -float("inf")  # type: ignore


class ExitCodeHandler:
    # TODO: Document how I function
    def __init__(self):
        self.allowed_exit_codes = self.generate_allowed_exit_codes()
        self.result_exit_codes = self.allowed_exit_codes[:-1]
        self.check_output_exit_code = self.allowed_exit_codes[-1]

    def scan(self, exit_code: int) -> ResultFromExitCode:
        if exit_code in self.allowed_exit_codes:
            if exit_code == self.check_output_exit_code:
                return ResultFromExitCode(ExitCodeEvent.CHECK_OUTPUT)
            else:
                associated_value = self.allowed_exit_codes.index(exit_code)
                return ResultFromExitCode(ExitCodeEvent.RESULT, associated_value)
        elif exit_code in SYSTEM_RESERVED_EXIT_CODES:
            return ResultFromExitCode(ExitCodeEvent.SYSTEM_ERROR)
        # It means that it IS used by grader but not chosen as a value
        elif exit_code in ALL_USED_EXIT_CODES:
            return ResultFromExitCode(ExitCodeEvent.CHEAT_ATTEMPT)
        else:
            raise ValueError(f"Exit code '{exit_code}' is not possible.")

    def get_formatted_exit_codes(self) -> Dict[str, str]:
        # Last exit code is for check_output
        formatted_result_exit_codes = ', '.join(str(r) for r in self.result_exit_codes)
        return {
            "RESULT_EXIT_CODES": formatted_result_exit_codes,
            "CHECK_OUTPUT_EXIT_CODE": str(self.check_output_exit_code)
        }

    @staticmethod
    def generate_allowed_exit_codes():
        used_exit_codes = ALL_USED_EXIT_CODES.copy()
        random.shuffle(used_exit_codes)
        return used_exit_codes[:ALLOWED_EXIT_CODE_COUNT]
