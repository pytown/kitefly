![Kitefly](doc/img/logo.png)

The KiteFly library allows you to generate Buildkite pipeline yaml using type-checked composable models, and also provides the ability to filter pipelines based on matching source files on monorepo pull requests.

## Installation

```
pip install kitefly
```

## Usage


Create a pipeline file in your repository (e.g. `generate_pipeline.py`). Here's a simple example:
```py
#!/usr/bin/env python
# File: generate_pipeline.py
from kitefly import Command, GitFilter, Group, Pipeline, Target, Wait

#
# 1. Define your Source Targets (Optional)
#
lib = Target.src('src/lib', 'src/lib-v2')
app = Target.src('src/app').prio(10)
app >> lib
py_files = Target('**/*.py')

coverage = Step('Collect code coverage', 'script/coverage-collector.sh')



#
# 2. Define the Pipeline
#

# You can inherit from Command to apply env vars and agents targeting to
# all steps with that class. Those class properties will be merged in reverse-MRO
class Linux(Command):
  env = {
    "PYTHON_PATH": "/usr/bin/python3"
  }
  agents = {
    "os": "linux"
  }

class LinuxHighCpu(Linux):
  agents = {
    "instance": "large"
  }


pipeline = Pipeline(
  Group(
    LinuxHighCpu(
      'Run app tests',
      'script/test-app.sh',
      targets=[target_app],
    ) << coverage,
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
  ) << coverage
  Wait(),
  Command(
    'Run pylint',
    './script/pylint.sh',
    targets=py_files,
    env={PYENV: "project-3.6.3"}
  ) << coverage,
  Command('Publish test artifacts ', './script/publish-test-results.sh')
)

#
# 3. Filter your pipeline against targets matching changes from base:
#
filtered = pipeline
if base_branch := os.getenv('BUILDKITE_BASE_BRANCH'):
  filtered = pipeline.filter(GitFilter(base_branch=base_branch))

#
# 4. Print out the Pipeline YAML
#
print(filtered.asyaml())
```

The pipeline can now be generated as the main executor step in Buildkite:
```
pip install kitefly
generate_pipeline.py | buildkite-agent upload
```

## About Filtering

Kitefly provides a model to associate build steps with source "targets", enabling filtering to run fewer builds. This is particularly useful for monorepos.

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
2. "Collect coverage" - since this step isn't bound to any targets

For each of the declared steps, a "key" field will automatically be generated based on the name of the step. Steps that declare a trigger on another step will have the relevant `depends_on` field set automatically on the triggered step. For example, the `coverage` step will be rendered after the "Run e2e" tests step (since that's the last one that triggers it) and before the Wait() step, and that `coverage` step will have 3 values on its `depends_on` field for the 3 test steps that trigger it. If any of those dependencies is not rendered in the pipeline, it will be automatically removed from the dependency list.

## License

[MIT](LICENSE.md)

