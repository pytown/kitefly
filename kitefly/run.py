

from .model import Pipeline

def run(pipeline: Pipeline):
  data = [s.asdict() for s in pipeline.flatten()]
  print(data)
  pass