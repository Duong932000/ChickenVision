from __future__ import annotations

import logging

import typer

from chickenvision.cli.dataset_cmd import dataset_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = typer.Typer(
    name="chickenvision",
    help="ChickenVision CLI — dataset, training, and inference stages.",
)
app.add_typer(dataset_app, name="dataset")


if __name__ == "__main__":
    app()
