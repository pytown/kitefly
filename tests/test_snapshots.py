import os

from kitefly import (
    AutomaticRetry,
    BuildAttributes,
    Pipeline,
    Command,
    Group,
    NoopFilter,
    Option,
    Plugin,
    Input,
    Target,
    TextField,
    SelectField,
    Trigger,
    Wait,
)
from kitefly.model.retry import ManualRetry

snapshot_count = {}


def check_snapshot(name: str, pipeline: Pipeline):
    snap_name = name
    if name not in snapshot_count:
        snapshot_count[name] = 0
    else:
        snapshot_count[name] += 1
        count = snapshot_count[name]
        snap_name += "-" + str(count)
    snap_name += ".yml"
    # pipeline = pipeline.filtered(GitFilter(base_branch="main"))
    output = pipeline.asyaml()
    snapshots = os.path.join(os.path.dirname(__file__), "__snapshots__")
    snap_file = os.path.join(snapshots, snap_name)
    os.makedirs(snapshots, exist_ok=True)
    if os.path.isfile(snap_file):
        with open(snap_file, encoding="utf8") as stream:
            content = stream.read()
            try:
                assert output == content
            except AssertionError:
                raise ValueError(
                    f"Snapshot does not match content: {snap_file}."
                    f" To reset the snapshot, run `rm {snap_file}`"
                )
    else:
        with open(snap_file, mode="w") as stream:
            stream.write(output)
        assert (
            False
        ), f"New snapshot written to {snap_file} -- run test again to verify\n"


def test_pipeline_one_step():
    check_snapshot("one-step", Pipeline(Command("Run Tests", "script/test.sh")))


def test_pipeline_group():
    check_snapshot(
        "group",
        Pipeline(
            Group(
                Command("Run Build", "script/build.sh"),
                Command("Run Tests", "script/test.sh"),
            )
        ),
    )


def test_pipeline_step_with_deps():
    check_snapshot(
        "group-with-deps",
        Pipeline(
            Group(
                Command("Run Build", "script/build.sh"),
                Command("Run Tests", "script/test.sh"),
            )
            << Command("Collect Results", "script/collect-results.sh")
        ),
    )


def test_full_example():
    test_results = Command("Collect Results", "script/collect-results.sh")

    class CommonCommand(Command):
        artifact_paths = ["build-artifacts/**"]

    class LinuxCommand(CommonCommand):
        agents = {"os": "linux"}

    class LinuxHighCpuCommand(LinuxCommand):
        agents = {"cores": 8}

    py_files = Target.src("**/*.py")
    md_files = Target.src("**/*.md")
    py_test_files = Target.src(r"**/test_*.py")
    py_test_files >> py_files

    check_snapshot(
        "full-example",
        Pipeline(
            Group(
                LinuxHighCpuCommand(
                    "Run Build",
                    "script/build.sh",
                    targets=[py_test_files],
                    plugins=[Plugin("coverage", {"token": "foo"})],
                    timeout_in_minutes=60,
                    env={"ENABLE_INSTRUMENTATION": "1"},
                ),
                LinuxCommand(
                    "Run Tests", "script/test.sh", parallelism=2, priority=100, soft_fail=True
                ),
                Command(
                    "Test docs",
                    "test-doc.sh",
                    targets=[md_files.prio(10)],
                    artifact_paths=["docs-generated/**"],
                    automatic_retries=[AutomaticRetry(1, exit_code=2)],
                    soft_fail=[2, 3],
                ),
            )
            << test_results,
            Wait(),
            Input(
                label="Get trigger input",
                prompt="Enter the password:",
                fields=[
                    TextField("password", "Password", hint="The shared team password"),
                    SelectField(
                        "build_type",
                        "Build Type",
                        options=[
                            Option("CI", "ci"),
                            Option("Local", "local"),
                        ],
                        hint="The shared team password",
                    ),
                ],
                blocked_state="running",
            ),
            Trigger(
                pipeline="my-pipe",
                build=BuildAttributes(
                    message="Automatic Build",
                    commit="HEAD",
                    branch="develop",
                    env={"FOO": 1},
                ),
                label="Run My Pipe",
                asynchronous=True,
            ),
            Wait(),
            Input(
                "Deployment Gate",
                "Enter 'deploy'",
                [TextField(key="confirmation", name="Confirmation")],
            ),
            CommonCommand(
                "Deploy",
                "scripts/deploy.sh",
                concurrency=1,
                concurrency_group="deployment",
                automatic_retries=2,
                manual_retry=ManualRetry(allowed=True, permit_on_passed=True),
                artifact_paths="build-artifacts/**;artifacts/**",
            ),
            Command("Skipped command", "skipped.sh", skip_reason="Needs to be fixed"),
        ).filtered(NoopFilter()),
    )
