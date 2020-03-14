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

# Navigation
* [Getting Started Guide](docs/getting_started.md)
* [Task Documentation](docs/tasks/README.md)
* [How to Contribute](docs/contribution.md)
