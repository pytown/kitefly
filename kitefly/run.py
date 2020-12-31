"""
Usage:
  kitefly <pipeline.py> [-b|--base-branch=<base-branch>]
"""
from yaml import dump as yaml_dump

from .model import Pipeline

VERSION = "0.1.0"

class Runner():
  def run(pipeline: Pipeline):
    steps = [s.asdict() for s in pipeline.steps()]
    output = {
      "steps": steps
    }
    print(yaml_dump(output))


def run(pipeline: Pipeline):
  Runner().run(pipeline)