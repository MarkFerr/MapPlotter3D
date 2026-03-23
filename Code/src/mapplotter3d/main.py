#import Files
import os
import logging
import sys
from pathlib import Path
import argparse


from mapplotter3d.mapplotter import run_mapplotter


def parse_args():
    parser = argparse.ArgumentParser(description="My example project")

    parser.add_argument("--data-path", required=True, help="Input file path")   #"C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Data\\Data\\municipality_test_data.csv"
    parser.add_argument("--location-column", default="municipality", type=str, help="Column in the data that lists the region names")
    parser.add_argument("--plot-column", default="population_test", type=str, help="Column that should be plotted")
    parser.add_argument("--logging-level", default=logging.INFO, type=int, help="Set logging level (0, 10, 20, 30, 40, 50)")

    return parser.parse_args()


def setup_logging(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    args = parse_args()

    setup_logging(args.logging_level)

    run_mapplotter(data_path=args.data_path, loc_column=args.location_column, plot_key=args.plot_column)



if __name__ == "__main__":
    main()