# kitefly

Dynamically generate Buildkite pipeline files with composable python models

## Installation

```
pip install kitefly
```

## Usage


Create a pipeline file in your repository (e.g. `my_pipeline.py`). Here's a simple example:
```
# File: my_pipeline.py
from kitefly import Step, Target, Wait, run


lib = Target('src/lib', 'src/lib-v2')
app = Target('src/app') >> (lib,)
py_files = Target('**/*.py')

test_collector = Step('Test Collector', 'script/test-collector.sh')

run(Pipeline(
  Step('Run app tests', 'script/test-app.sh', targets=target_app) >> test_collector,
  Step('Run library tests', 'script/test-lib.sh', targets=target_lib) >> test_collector,
  Step('Run e2e tests', './script/e2e.sh', targets=(target_app,target_lib)) >> test_collector,
  Wait(),
  Step('Run pylint', './script/pylint.sh', targets=py_files, env={PYENV: "project-3.6.3"}) >> test_collector,
  Step('Publish test artifacts ', './script/publish-test-results.sh')
))
```

The pipeline can now be generated as follows within Buildkite:

```
kitefly ./my_pipeline.py | buildkite-agent upload
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

A full list of `kitefly` execution options can be found by executing `kitefly --help`, and can also be found in [API.md](API.md) along with the full API listing of `kitefly` modules.


## License

[MIT](LICENSE.md)

