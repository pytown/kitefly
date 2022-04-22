[![lint and tests](https://github.com/pytown/kitefly/actions/workflows/test.yml/badge.svg)](https://github.com/pytown/kitefly/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/pytown/kitefly/branch/main/graph/badge.svg?token=Y4EWTI5ZYE)](https://codecov.io/gh/pytown/kitefly)

![Kitefly](doc/img/logo.png)

The Kitefly python library can be used to generate Buildkite pipeline YAML using type-checked composable classes. Additionally, a filter mechanism is available which can be used to reduce the number of jobs in pull requests for mono-repos, or other similar applications.

## Installation

```
pip install kitefly
```

## Usage

Create a pipeline file in your repository (e.g. `generate_pipeline.py`). Here's a simple example:

```
#!/usr/bin/env python
# File: generate_pipeline.py

from kitefly import *

# 1. Define your Source Targets (Optional)

lib = Target.src('src/lib', 'src/lib-v2')
app = Target.src('src/app').prio(10)
app >> lib
py_files = Target('**/*.py')


# 2. Define the Pipeline
# You can inherit from Command to apply env vars and agents targeting to
# all steps with that class. Those class properties will be merged in reverse-MRO.

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

# If you want to declare dependencies, you can create variables for certain
# steps to be used below.
coverage = Command('Collect and publish code coverage', 'script/coverage-collector.sh')

app_tests = LinuxHighCpu('Run app tests', 'script/test-app.sh', targets=[app])
lib_tests = Linux('Run library tests', 'script/test-lib.sh', targets=[lib])
e2e_tests = Command('Run E2E Tests', 'script/e2e.sh', targets=[app])
lint = Command('Run pylint', './script/pylint.sh', targets=py_files, env={PYENV_VERSION: "project-3.6.3"})

lint_phase = Group([lint], label='Lint') 
test_phase = Group([app_tests, lib_tests, e2e_tests], label='Test')
test_phase >> lint_phase

pipeline = Pipeline([
  lint_phase,
  test_phase,
  Wait(),
  Command('Publish test artifacts ', './script/publish-test-artifacts.sh')
])

# 3. Filter your pipeline against targets matching changes from base (optional):
#    By default, `GitFilter` uses the BUILDKITE_PULL_REQUEST_BASE_BRANCH environmental variable.
filtered = pipeline.filter(GitFilter())

# 4. Print out the Pipeline YAML. Alternatively, you could write it to a file
#    and then upload it using `buildkite-agent pipeline upload [file]`
#
print(filtered.asyaml())
```

The pipeline can now be generated as the main executor step in Buildkite:

```
pip install kitefly
generate_pipeline.py | buildkite-agent pipeline upload
```

## About Filtering

Kitefly provides a model to associate build steps with source "targets", enabling filtering to run fewer builds. This is particularly useful for monorepos.

For example, if the command `git ls-files <buildkite-branch>..<base-branch>` outputs:

```
src/lib/util.ts
```

Then the `target_lib` target will match, since its filepath spec includes `src/lib`, and `target_app` will also be included in the list of targets since `target_app` has a target dependency on `target_lib`.

If, on the other hand, the list of files reported by git is:

```
src/infra/tool.py
```

Then only the `py_files` target will match, and so only steps targeting `py_files` will be included in the pipeline, along with steps that do not specify any target.


## License

[MIT](LICENSE.md)
