![Kitefly](doc/img/logo.png)

Dynamically generate Buildkite pipeline files with composable python models

## Installation

```
pip install kitefly
```

## Usage


Create a pipeline file in your repository (e.g. `my_pipeline.py`). Here's a simple example:
```py
# File: my_pipeline.py
from kitefly import Command, Group, Target, Wait, run

lib = Target(sources=('src/lib', 'src/lib-v2'))
app = Target(sources='src/app', priority=10)
app >> lib
py_files = Target('**/*.py')

test_results = Step('Collect test results', 'script/test-collector.sh')
coverage = Step('Collect code coverage', 'script/coverage-collector.sh')

# You can inherit from Command to apply env + agents targeting to
# all steps with that class. Those class properties will be merged in reverse-MRO
class Linux(Command):
  env = {
    "PYTHON_PATH": "/usr/bin/python3"
  }
  agents = {
    "os": "linux"
  }

run(Pipeline(
  Group(
    Linux(
      'Run app tests',
      'script/test-app.sh',
      targets=[target_app],
    ) >> coverage,
    Linux(
      'Run library tests',
      'script/test-lib.sh',
      targets=[target_lib],
    ),
    Command(
      'Run e2e tests',
      'script/e2e.sh',
      targets=[target_app, target_lib]
    )
  ) >> test_results,
  Wait(),
  Command(
    'Run pylint',
    './script/pylint.sh',
    targets=py_files,
    env={PYENV: "project-3.6.3"}
  ) >> test_results,
  Command('Publish test artifacts ', './script/publish-test-results.sh')
))
```

The pipeline can now be generated as follows within Buildkite:

```
python my_pipeline.py | buildkite-agent upload
```

By default, `kitefly` will use the base branch file comparison based on Buildkite ENV variables to filter the list of steps to only include those matching affected "Targets", i.e. those whose file lists from the git branch comparison match the file specs of the given targets.

For example, if the `git ls-files <buildkite-branch>..<base-branch>` is:
```
src/lib/util.ts
```

Then the `target_lib` target will match, since its filepath spec includes `src/lib`, and `target_app` will also be included in the list of targets since `target_app` has a target dependency on `target_lib`.

If, on the other hand, the list of files reported by git is:
```
src/infra/tool.py
```

Then only the `py_files` target will match, and so only the last 2 steps in the provided pipeline will be included in the output:

1. "Run pylint" - since the `py_files` target matches
2. "Publish test artifacts" - since this step isn't bound to any targets

For each of the declared steps, a "key" field will automatically be generated based on the name of the step. Steps that declare a trigger on another step will have the relevant `depends_on` field set automatically on the triggered step. For example, the `test_collector` step will be rendered after the "Run e2e" tests step (since that's the last one that triggers it) and before the Wait() step, and that `test_collector` step will have 3 values on its `depends_on` field for the 3 test steps that trigger it. If any of those dependencies is not rendered in the pipeline, it will be automatically removed from the dependency list.

For non-Pull-Request builds where there is no declared Buildkite base branch variable, the full pipeline will be executed by default. This behavior can be controlled by various options passed to the `kitefly` executable.

A full listing of models and documentation can be seen at [API.md](API.md).


## License

[MIT](LICENSE.md)

