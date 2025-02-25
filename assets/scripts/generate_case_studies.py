# Flake8: noqa
import argparse, os, asyncio


async def main(args):
    print("Output Directory:", args.output)
    print("Source Dataset:", args.source)
    print("Destination Dataset:", args.dest)
    print("Max Workers:", args.max_workers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate dark thoughts case studies")
    parser.add_argument(
        "--output",
        default=os.getcwd(),
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--source",
        default="DataTonic/dark_thoughts_stakeholders_80",
        help="Source HuggingFace dataset",
    )
    parser.add_argument(
        "--destination",
        default="scaleway_r1_dark_thoughts_casestudies",
        help="Destination dataset name to push to Hub",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum number of concurrent workers (default: 5)",
    )
    args = parser.parse_args()
    asyncio.run(main(args))
