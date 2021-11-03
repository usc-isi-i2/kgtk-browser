"""
Run the KGTK-Browser Flask server

Optional: open a browser window with kgtk-browser url
"""

from argparse import Namespace, SUPPRESS
import typing

from kgtk.cli_argparse import KGTKArgumentParser, KGTKFiles


# Define the name of the command and its alias.
BROWSER_COMMAND: str = "browser"
BROWSE_COMMAND: str = "browse"


def parser():
    return {
        'aliases': [ BROWSE_COMMAND ],
        'help': 'Run the KGTK-Browser Flask app.',
        'description': 'Open a new browser with the KGTK-Browser app running.',
    }


def add_arguments_extended(parser: KGTKArgumentParser, parsed_shared_args: Namespace):
    """
    Parse arguments
    Args:
        parser (argparse.ArgumentParser)
    """
    from kgtk.utils.argparsehelpers import optional_bool

    # These special shared aruments inticate whether the `--expert` option
    # was supplied and the command name that was used.
    _expert: bool = parsed_shared_args._expert
    _command: str = parsed_shared_args._command

    # This helper function makes it easy to suppress options from
    # The help message.  The options are still there, and initialize
    # what they need to initialize.
    def h(msg: str)->str:
        if _expert:
            return msg
        else:
            return SUPPRESS


def run(
        errors_to_stdout: bool = False,
        errors_to_stderr: bool = True,
        show_options: bool = False,
        verbose: bool = False,
        very_verbose: bool = False,

        **kwargs # Whatever KgtkFileOptions and KgtkValueOptions want.
)->int:
    # import modules locally
    from pathlib import Path
    import simplejson as json
    import os, sys
    import typing

    from kgtk.exceptions import KGTKException

    # Select where to send error messages, defaulting to stderr.
    error_file: typing.TextIO = sys.stdout if errors_to_stdout else sys.stderr

    # Show the final option structures for debugging and documentation.
    if show_options:
        print("--input-file=%s" % repr(str(input_file_path)), file=error_file, flush=True)
        print("--output-file=%s" % repr(str(output_file_path)), file=error_file, flush=True)

        idbuilder_options.show(out=error_file)
        print("=======", file=error_file, flush=True)

    try:

        os.environ["FLASK_APP"] = "kgtk_browser_app.py"
        os.environ["FLASK_ENV"] = "development"
        os.environ["KGTK_BROWSER_CONFIG"] = "kgtk_browser_config.py"

        os.system("flask run --host 0.0.0.0 --port 5000")

        return 0

    except SystemExit as e:
        raise KGTKException("Exit requested")
    except Exception as e:
        raise KGTKException(str(e))
