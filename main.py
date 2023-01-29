import argparse
import os
import shutil
import sys
import logging
if hasattr(shutil, "which"):
    _which = shutil.which
else:
    # Python 2 fallback
    from distutils import spawn

    _which = spawn.find_executable  # type: ignore[assignment]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def find_executable( p):
    if os.path.isfile(p):
        return p
    return _which(p)


def _add_bootstrap_to_pythonpath(root_dir, bootstrap_dir):
    """
    Add our bootstrap directory to the head of $PYTHONPATH to ensure
    it is loaded before program code
    """
    python_path = os.environ.get("PYTHONPATH", "")

    if python_path:
        new_path = "%s%s%s" % (bootstrap_dir, os.path.pathsep, os.environ["PYTHONPATH"])
        os.environ["PYTHONPATH"] = new_path
    else:
        os.environ["PYTHONPATH"] = "%s:%s" % (root_dir, bootstrap_dir)


# entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="",
        prog="blabla",
        usage="blabla <your usual python command>",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, type=str, help="Command string to execute.")
    args = parser.parse_args()

    # Find the executable path
    executable = find_executable(args.command[0])
    if executable is None:
        print("ddtrace-run: failed to find executable '%s'.\n" % args.command[0])
        parser.print_usage()
        sys.exit(1)

    root_dir = os.path.dirname(__file__)
    print("ddtrace root: %s", root_dir)

    bootstrap_dir = os.path.join(root_dir, "bootstrap")
    print("ddtrace bootstrap: %s", bootstrap_dir)

    _add_bootstrap_to_pythonpath(root_dir, bootstrap_dir)
    print("PYTHONPATH: %s", os.environ["PYTHONPATH"])
    print("sys.path: %s", sys.path)

    try:
        os.execl(executable, executable, *args.command[1:])
    except PermissionError:
        print("ddtrace-run: permission error while launching '%s'" % executable)
        print("Did you mean `ddtrace-run python %s`?" % executable)
        sys.exit(1)
    except Exception:
        print("ddtrace-run: error launching '%s'" % executable)
        raise