from kitefly import Pipeline, Command, generate

import os

snapshot_count = {}

def check_snapshot(name: str, pipeline: Pipeline):
  snap_name = name
  if name not in snapshot_count:
    snapshot_count[name] = 0
  else:
    snapshot_count[name] += 1
    count = snapshot_count[name]
    snap_name += "-" + count
  snap_name += '.yml'
  output = generate(pipeline=pipeline)
  snapshots = os.path.join(os.path.dirname(__file__), '__snapshots__')
  snap_file = os.path.join(snapshots, snap_name)
  os.makedirs(snapshots, exist_ok=True)
  if os.path.isfile(snap_file):
    with open(snap_file, encoding='utf8') as stream:
      content = stream.read()
      assert content == output
  else:
    with open(snap_file, mode="w") as stream:
      stream.write(output)
    assert False, f"New snapshot written to {snap_file} -- run test again to verify"


def test_pipeline_one_step():
  check_snapshot('one-step', Pipeline(Command("Run Tests", "script/test.sh")))