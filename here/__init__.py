
__version__ = "0.5.0"

import pathlib
import argparse
import subprocess

import pyperclip as clipboard
import keyboard
import colex
from actus import info, warn, error


class ParserArgs(argparse.Namespace):
    silent: bool
    verbose: bool
    end: str
    where_mode: bool
    folder_mode: bool
    change_mode: bool
    no_copy_mode: bool


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="here",
        usage="Copy 'here' path to clipboard"
    )
    parser.add_argument("-v", "--version",
                        action="version",
                        version=f"%(prog)s: v{__version__}")
    parser.add_argument("-f", "--folder",
                        action="store_true",
                        dest="folder_mode")
    parser.add_argument("-w", "--from-where",
                        action="store_true",
                        dest="where_mode")
    parser.add_argument("-d", "--change-directory",
                        action="store_true",
                        dest="change_mode")
    parser.add_argument("-n", "--no-copy",
                        action="store_true",
                        dest="no_copy_mode")
    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("--verbose",
                            action="store_true")
    print_group.add_argument("--silent",
                            action="store_true")
    parser.add_argument("end",
                        nargs="?",
                        default=".",
                        help="Relative path to join with current working directory path")
    args = ParserArgs()
    parser.parse_args(namespace=args)

    # TODO: handle select of multipath results

    if args.where_mode:
        if args.end == ".":
            if not args.silent:
                error('Cannot search for $["."]. Argument $[end] required')
                info("Caused by flag $[-w]/$[--from-where]")
            return 1 # invalid search
        result = subprocess.run(["where", args.end],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        if result.returncode != 0:
            if not args.silent:
                error(f"Could not find $[{args.end}]")
                info("Caused by flag $[-w]/$[--from-where]")
            return 2 # seach unsuccessful
        location = result.stdout.rstrip("\n ")
        absolute_path = (
            pathlib.Path(location)
            .resolve()
        )
    else:
        absolute_path = (
            pathlib.Path
            .cwd()
            .joinpath(args.end)
            .resolve()
        )
    if args.folder_mode:
        if absolute_path.is_file(): # remove file part
            absolute_path = absolute_path.parent

    if not args.silent:
        if args.verbose:
            colored_path = colex.colorize(str(absolute_path), colex.UNDERLINE + colex.SALMON)
            if not args.no_copy_mode:
                info(f"Copying to clipboard$[:] {colored_path}")
            else:
                info(f"Found$[:] {colored_path}")
        else:
            print(colex.colorize(str(absolute_path), colex.SALMON))

    if not args.no_copy_mode:
        clipboard.copy(str(absolute_path))
    elif args.verbose:
        info("Flag $[-n]/$[--no-copy] is present, $[ignoring copying to clipboard]")

    if args.change_mode:
        if not absolute_path.is_dir():
            if not args.silent:
                warn(f"$[{absolute_path}] is not a $[directory], and can therefore $[not change]!")
            return 3 # requires folder path to change
        if not args.silent:
            if args.verbose:
                info(f"Preparing $[cd {absolute_path}]...")
        keyboard.write(f'cd "{absolute_path}"')
        keyboard.press_and_release("enter")
    return 0
