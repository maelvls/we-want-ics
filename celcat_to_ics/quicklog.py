""" Quicklog. A helper class to facilitate logging.

* Provides easy setup and tear-down of a timestamped event log.
* Provides helper methods that simultaneously log to the event log and
  to the console (based on settable 'logging_levep' and 'print_level').
* Provides colorization of (console printed) log level designations
  (WARNING, INFO, etc.).

Author: Eric Moyer
"""

# Linter Directives
#     General
#         pylint: disable=locally-disabled, line-too-long, import-error, no-name-in-module
#         pylint: disable=locally-disabled, too-many-locals, too-many-branches, too-many-statements
#         pylint: disable=locally-disabled, too-many-instance-attributes
#     Specific
#         pylint: disable=locally-disabled, too-many-arguments

from __future__ import print_function
import sys
import logging
from colorama import init, Fore

init(autoreset=True)


class Quicklog(object):
    def __init__(
        self,
        application_name,
        enable_colored_printing=True,
        version=None,
        log_filename="output.log",
        logging_level=logging.INFO,
        print_level=logging.WARNING,
        enable_colored_logging=False,
    ):

        self._application_name = application_name
        self._version = version
        self._enable_colored_printing = enable_colored_printing
        self._enable_colored_logging = enable_colored_logging
        self._print_level = print_level
        self._log_filename = log_filename
        self._logging_level = logging_level
        self._color_clear = Fore.RESET
        self._log_color = {
            logging.DEBUG: Fore.BLUE,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }
        self._log_level_name = {
            logging.DEBUG: "DEBUG",
            logging.INFO: "INFO",
            logging.WARNING: "WARNING",
            logging.ERROR: "ERROR",
            logging.CRITICAL: "CRITICAL",
        }
        if enable_colored_logging:
            color = Fore.YELLOW
            color_clear = Fore.RESET
        else:
            color = ""
            color_clear = ""
        logging.basicConfig(
            filename=log_filename,
            level=logging_level,
            format=color + "%(asctime)s" + color_clear + " %(message)s",
        )

    def debug_is_enabled(self):
        """True if current logging level includes DEBUG"""
        return self._logging_level <= logging.DEBUG

    def begin(self, show=True):
        # Log execution start
        logging.info(
            "------------------------------ BEGIN ------------------------------ "
        )

        # Print/log applicaiton/version info
        message = self._application_name
        if self._version:
            message += ", Version {}".format(self._version)
        logging.info(message)
        if show:
            print(message)
            print("---------------------------------------")
            print('(Logging to: "{}")'.format(self._log_filename))

    def end(self):
        # Log execution end
        logging.info(
            "------------------------------- END ------------------------------- "
        )

    def debug(self, message):
        self.log(message, logging.DEBUG)

    def info(self, message):
        self.log(message, logging.INFO)

    def warning(self, message):
        self.log(message, logging.WARNING)

    def error(self, message):
        self.log(message, logging.ERROR)

    def critical(self, message):
        self.log(message, logging.CRITICAL)

    def critical_quiet(self, message):
        # Log but do not print
        logging.log(logging.CRITICAL, "CRITICAL: {}".format(message))

    def lprint(self, message):
        """Log and print"""
        print(message)
        self.log(message, logging.INFO)

    def log(self, message, log_level):
        log_prefix = self._log_level_name[log_level]
        if self._log_color[log_level]:
            color = self._log_color[log_level]
            color_clear = self._color_clear
        else:
            color = ""
            color_clear = ""

        print_prefix = log_prefix
        logging.log(
            log_level,
            "{}{}{}: {}".format(
                color if self._enable_colored_logging else "",
                print_prefix,
                color_clear if self._enable_colored_logging else "",
                message,
            ),
        )

        if log_level >= self._print_level:
            print(
                "{}{}{}: {}".format(
                    color if self._enable_colored_printing else "",
                    print_prefix,
                    color_clear if self._enable_colored_printing else "",
                    # TODO: Handle unicode to stdout.  For now, unprintable unicode is replaced with "?" using .encode() with errors='replace'
                    # See: http://stackoverflow.com/questions/14630288/unicodeencodeerror-charmap-codec-cant-encode-character-maps-to-undefined
                    message.encode(sys.stdout.encoding, errors="replace").decode(
                        "utf-8"
                    ),
                )
            )
