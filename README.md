![Mule logo](docs/img/mule-logo.png)

# Mule

Mule is a generalized automation framework for organizing the execution of defined automation in a declarative yaml format. To consume it, a user only needs to write a yaml file that defines tasks they wish to execute and jobs that execute their order. Below is an example of a basic mule.yaml file. For more information, see our [getting started guide](docs/getting_started.md)!

```yaml
tasks:
- task: Echo
  name: A
  message: A

jobs:
  job-a:
    tasks:
    - Echo.A
```

## Install

To install mule using pip, use:

```
pip install mulecli
```

## Git Hooks

There are two custom `pre-commit` hooks that can be easily installed by running the `install.sh` script found within the `./scripts/hooks/` directory:

```
./scripts/hooks/install.sh
```

These will install two local `pre-commit` hooks in `./.git/config`. The hooks have two dependencies, [pytest] and [pycodestyle]. There are no default filters for [pycodestyle], that is left up to the developer.

`pytest` is already a dependency of `mule`. To install `pycodestyle`:

```
python -m pip pycodestyle
```

Once installed, they can be ignored when committing, if needed:

```
git commit --no-verify
```

# Navigation
* [Getting Started Guide](docs/getting_started.md)
* [Task Documentation](docs/tasks/README.md)
* [How to Contribute](docs/contribution.md)

[pytest](https://pypi.org/project/pytest/)
[pycodestyle](https://pypi.org/project/pycodestyle/)

