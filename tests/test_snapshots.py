from kitefly import Pipeline, Command, Group, Input, TextField, Wait

import os

snapshot_count = {}

def check_snapshot(name: str, pipeline: Pipeline):
  snap_name = name
  if name not in snapshot_count:
    snapshot_count[name] = 0
  else:
    snapshot_count[name] += 1
    count = snapshot_count[name]
    snap_name += "-" + str(count)
  snap_name += '.yml'
  output = pipeline.asyaml()
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

def test_pipeline_group():
  check_snapshot('group', Pipeline(Group(
    Command("Run Build", "script/build.sh"),
    Command("Run Tests", "script/test.sh"),
  )))

def test_pipeline_step_with_deps():
  check_snapshot('group-with-deps', Pipeline(
    Group(
      Command("Run Build", "script/build.sh"),
      Command("Run Tests", "script/test.sh")
    ) << Command("Collect Results", "script/collect-results.sh")
  ))

def test_full_example():
  test_results = Command("Collect Results", "script/collect-results.sh")

  class CommonCommand(Command):
    artifact_paths = ["build-artifacts/**"]

  class LinuxCommand(CommonCommand):
    agents = {"os": "linux"}

  class LinuxHighCpuCommand(LinuxCommand):
    agents = {"cores": 8}

  check_snapshot('full-example', Pipeline(
    Group(
      LinuxHighCpuCommand("Run Build", "script/build.sh"),
      LinuxCommand("Run Tests", "script/test.sh", parallelism=2)
    ) << Command("Collect Results", "script/collect-results.sh"),
    Wait(),
    Input("Deployment Gate", "Enter 'deploy'", [TextField(key="confirmation", name="Confirmation")]),
    CommonCommand("Deploy", "scripts/deploy.sh", concurrency=1, concurrency_group="deployment")
  ))