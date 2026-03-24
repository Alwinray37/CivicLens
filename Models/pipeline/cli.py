import argparse
import datetime
import sys

from pipeline.config import load_config
from pipeline.exceptions import PipelineError
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.validation import run_preflight_checks


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="council-pipeline",
        description="Download, transcribe, and process LA City Council meetings.",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--latest",
        action="store_true",
        help="Process the most recent meeting for the current calendar year (default behavior).",
    )
    group.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Process the meeting on a specific date.",
    )

    parser.add_argument(
        "--config",
        metavar="PATH",
        default=None,
        help="Path to config.yaml. Defaults to config.yaml in the current directory.",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.date:
        try:
            datetime.date.fromisoformat(args.date)
        except ValueError:
            print(
                f"Error: Invalid date '{args.date}'. Expected format: YYYY-MM-DD.",
                file=sys.stderr,
            )
            sys.exit(1)
        config.target_date = args.date
        config.meeting_year = int(args.date[:4])
    else:
        # --latest or bare invocation: use current calendar year
        config.meeting_year = datetime.date.today().year

    try:
        run_preflight_checks()
    except PipelineError as e:
        print(f"Pre-flight check failed:\n{e}", file=sys.stderr)
        sys.exit(1)

    orchestrator = PipelineOrchestrator(config)
    orchestrator.execute()
