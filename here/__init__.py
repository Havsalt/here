"""
here
----

Copy 'here' path to clipboard
"""

from __future__ import annotations

__version__ = "0.7.1"

import pathlib
import argparse
import subprocess

import pyperclip as clipboard
import keyboard
import colex
from actus import info, warn, error, LogSection, Style


class ParserArgs(argparse.Namespace):
    where_mode: bool
    folder_mode: bool
    change_mode: bool
    escape_backslash: bool
    no_copy_mode: bool
    no_color_mode: bool
    silent: bool
    verbose: bool
    segment: str


show_path = LogSection(
    "",
    left_deco="",
    right_deco="",
    label_end="",
    indent_deco="",
    indent_delimiter="",
    style=Style(
        text=colex.SALMON,
        highlight=colex.LIGHT_SALMON
    )
)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="here",
        description="Copy 'here' path to clipboard",
        add_help=False
    )
    parser.add_argument("-h", "--help",
                        action="help",
                        help="Show this help message and exit",
                        default=argparse.SUPPRESS)
    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"%(prog)s: v{__version__}",
                        help="Show `%(prog)s` version number and exit")
    parser.add_argument("-f", "--folder",
                        action="store_true",
                        dest="folder_mode",
                        help="Get folder component of result")
    parser.add_argument("-w", "--from-where",
                        action="store_true",
                        dest="where_mode",
                        help="Use `where` command to search")
    parser.add_argument("-d", "--change-directory",
                        action="store_true",
                        dest="change_mode",
                        help="Set current working directory to result (schedule)")
    parser.add_argument("-e", "--escape-backslash",
                        action="store_true",
                        dest="escape_backslash",
                        help="Escape backslashes (\\ -> \\\\)")
    parser.add_argument("-n", "--no-copy",
                        action="store_true",
                        dest="no_copy_mode",
                        help="Prevent copy to clipboard")
    parser.add_argument("-c", "--no-color",
                        action="store_true",
                        dest="no_color_mode",
                        help="Suppress color")
    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("--verbose",
                             action="store_true",
                             help="Display more info during execution")
    print_group.add_argument("--silent",
                             action="store_true",
                             help="Display less info during execution")
    parser.add_argument("segment",
                        nargs="?",
                        default=".",
                        help="Join with cwd, or use as search (with -w/--from-where)")
    args = ParserArgs()
    parser.parse_args(namespace=args)

    if args.no_color_mode:
        info.disable_color()
        warn.disable_color()
        error.disable_color()
        show_path.disable_color()
    
    if args.silent:
        info.disable_output()
        warn.disable_output()
        error.disable_output()
        show_path.disable_output()
    
    # TODO: handle select of multipath results in -w mode

    absolute_path: pathlib.Path # result of long if-else block
    if args.where_mode:
        if args.segment == ".":
            error('Cannot search for $["."]. Argument $[segment] required')
            info("Caused by flag $[-w]/$[--from-where]")
            return 1 # invalid search
        result = subprocess.run(["where", args.segment],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        if result.returncode != 0:
            error(f"Could not find $[{args.segment}]")
            info("Caused by flag $[-w]/$[--from-where]")
            return 2 # search unsuccessful
        location = result.stdout.rstrip("\n ")
        absolute_path = (
            pathlib.Path(location)
            .resolve()
        )
        if args.verbose:
            info(f'Search $["{args.segment}"] found $[{location}]')
    else:
        absolute_path = (
            pathlib.Path
            .cwd()
            .joinpath(args.segment)
            .resolve()
        )

    if args.folder_mode:
        if absolute_path.is_file(): # remove file part
            absolute_path = absolute_path.parent
    
    visual_path = (
        str(absolute_path)
        if not args.escape_backslash
        else str(absolute_path).replace("\\", "\\\\")
    )

    if args.verbose:
        color = (
            colex.UNDERLINE + colex.SALMON
            if not args.no_color_mode
            else colex.NONE
        )
        path = (
            colex.colorize(visual_path, color)
            if not args.no_color_mode
            else visual_path
        )
        if not args.no_copy_mode:
            info(f"Copying to clipboard$[:] {path}")
        else:
            info(f"Found$[:] {path}")
    else:
        show_path(visual_path)

    if not args.no_copy_mode:
        clipboard.copy(visual_path)
    elif args.verbose:
        info("Flag $[-n]/$[--no-copy] is present, $[ignoring copying to clipboard]")

    if args.change_mode:
        if not absolute_path.is_dir():
            warn(f"$[{absolute_path}] is not a $[directory], and can therefore $[not change]!")
            return 3 # requires folder path to change
        if args.verbose:
            info(f"Preparing $[cd {absolute_path}]...")
        keyboard.write(f'cd "{absolute_path}"')
        keyboard.press_and_release("enter")
    return 0
