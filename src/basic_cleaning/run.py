#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading and reading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()
    df = pd.read_csv(artifact_path, low_memory=False)

    logger.info("Dropping outliers")
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Convert last_review to datetime")
    df["last_review"] = pd.to_datetime(df["last_review"])

    logger.info("Save the results")
    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This stage cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name of the input artifact",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The type of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="The minimum price of rentals",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="The maximum price of rentals",
        required=True,
    )

    args = parser.parse_args()

    go(args)
