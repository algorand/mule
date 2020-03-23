# What is Mule?

Mule is a generalized automation framework for organizing the execution of defined automation in a declarative yaml format. For some context into why a tool like this is useful, we will explore the problem it is attempting to solve.

## The problem

Today there are hundreds, or even thousands, of tools on the market that are very good at executing very specific actions that are useful as part of an application's CICD process. The problem is that in order to use these tools, engineers need to write scripts that execute the features they need, while taking very special care that they execute them in the correct order. 

In most cases, this leads to brittle scripts that are tightly coupled to the application the developer is working on. At [Algorand](https://www.algorand.com/), we work on many different stacks to ensure that developers can consume all of the great features we provide on our platform. Therefore, tightly coupled scripts will not work for us at scale.

To solve this problem, we needed a tool that can meet the following conditions:

* Automation is decoupled from project repositories
* Automation can be consumed in a convenient way
* Automation is consistently executed by both users and our CICD process

There are a few pipeline technologies that almost meet all three of these conditions. The issue we have with using these options is that we do not wish to be married to any one pipeline technology, and also there are many things we would like to automate that do not need to be part of an application pipeline. Therefore, we decided these options were not quite convenient enough for us.

There are a few tools on the market that meet two of the three conditions, but most of these require either entrypoint scripts in the application repositories, which fails the first condition, or learning a new syntax that isn't simple or lightweight enough, which fails the third condition. Some combinations of these tools could manage to meet all three conditions, but we felt that their feature sets would be too diverse for the simple use case we were looking for.

After considering these options we decided to explore building our own solution to this problem.

## The solution

This solution is called Mule. Mule is a framework that generalizes the concept of a unit of automation, and allows you to organize their execution through an intuitive, declarative yaml format. Below is an explanation of how this abstraction provided by Mule meets the stated conditions:

* Automation is decoupled from project repositories
  * It allows users to define automated tasks as python scripts in one centralized location without any need for scripts in the application repositories.
* Automation can be consumed in a convenient way
  * It provides a simple, intuitive yaml language for declaring configurations for automated tasks and their execution order.
* Automation is consistently executed by both users and our CICD process
  * It provides a cli that can consume any valid mule yaml file and execute the automated tasks the same way everywhere

This abstraction has helped us to start organizing our CICD process and given us confidence that we can perform the time consuming effort of automating a task exactly once so that we can focus more time on building the Algorand network.

# Concepts

Before getting into how to use mule to execute automation, the following docs will introduce you to the key concepts of the Mule framework.

## Tasks

A task is an individual unit of automation. You can make a task for any activity you would like to automate. For a list of currently available tasks, see our [task documentation](tasks/README.md).

## Jobs

A job is a series of executable tasks, and a task itself for that matter. When you provide a job with a list of tasks, the job handles evaluating the chain of dependencies of the tasks you would like to execute and guarantees that all tasks and its dependencies are executed once in the order that they are needed.

# How to use Mule

## Introduction

In this section we will provide a series of examples to help you get used to the syntax used in a mule.yaml.

```yaml
tasks:
- task: Echo
  message: Message for the console

jobs:
  job-a:
    tasks:
    - Echo
```

Above is a mule config file that lists one task and one job.

- The tasks field is to document task configurations that are needed to execute jobs. It takes a list of maps (dicts in python) that are used to initialize your tasks -- keep in mind that every task configuration must have a task field set -- and is used by mule to loop through the task you wish to initialize.
- Every other field is a configuration for your task. In this example, we have one task called Echo, which simply prints out "Message for the console".

Next you have your jobs field. This is where you define jobs and provide them with a list of tasks you wish to execute when the job is invoked. The list in the job's tasks field contains the ids of the predefined tasks, which in this case is just the task definition.

When job-a is invoked, we see the following response:

```
$ mule -f path/to/mule.yaml job-a
Message for the console
```

And there we have our first mule job! Now we will look at a more interesting example.

## Task Dependencies

```yaml
tasks:
- task: Echo
  name: A
  message: Message for the console
- task: Echo
  name: B
  message: Another message for the console
  dependencies: Echo.A


jobs:
  job-b:
    tasks:
    - Echo.B
```

Now we have two tasks that we are defining. The first is an Echo task that prints out "Message for the console" and the second is an Echo task that prints out "Another message for the console". Since we are using two tasks who use the same task definition, we must provide a name field to each that differentiates them. When a name field is introduced to a task, its id becomes `task_definition.name`.

One more interesting thing here is the dependencies field in Echo.B. This field is used to declare that a task depends on another task. This way, when the task is executed inside of a job, any other task it depends on will be executed as well. This field can either be a space delimited string, or a yaml list of strings. Keep in mind of the order you arrange these dependencies, since the dependencies will be executed in the order you introduce them in here.

When job-b is invoked, we see the following response:

```
$ mule -f path/to/mule.yaml job-b   
Message for the console
Another message for the console
```

One more thing to note is that this file is logically equivalent to the following mule.yaml.

```yaml
tasks:
- task: Echo
  name: A
  message: Message for the console
- task: Echo
  name: B
  message: Another message for the console
  dependencies: Echo.A


jobs:
  job-b:
    tasks:
    - Echo.A
    - Echo.B
```

No matter the arrangement of tasks, Mule will evaluate the chain of dependent tasks that need to be executed such that tasks get executed once in the order they are needed.

Next, we will look into how you can parameterize your tasks.

## Job configs

Job configs are a way to set fields in your mule.yaml that will overwrite fields set in your task configurations. This way, you can define tasks that can work differently in different jobs.

```yaml
tasks:
- task: Echo
  name: A
  message: Message for the console


jobs:
  job-a:
    configs:
      message: Another message for the console
    tasks:
    - Echo.A
```

Here we have the same Echo task from the first example, but in job-a we have added a configs field. This configs field takes a map, and this can be used to overwrite fields of the same name in the tasks you have defined. Because here we are overwriting the message field in all of our tasks, we will see something different when we execute job-a.

```
$ mule -f path/to/mule.yaml job-a
Another message for the console
```

Now since our Echo task's message field has been overwritten, we are seeing mule print out "Another message for the console". We may offer more sophisticated ways to overwrite task configs in the future, but for now it's important to be careful when selecting fields that you would like to overwrite so that you do not see unintended consequences in your jobs.

Another thing you can do in a jobs config is set values using your system's environment variables.

```yaml
tasks:
- task: Echo
  name: A
  message: A


jobs:
  job-a:
    configs:
      message: ${ECHO_A}
    tasks:
    - Echo.A
```

Now our Echo task will print out the contents of the ECHO_A environment variable.

```
$ export ECHO_A='Message for the console'
$ mule -f path/to/mule.yaml job-a
Message for the console
```

Now that we can use jobs to parameterize tasks, let's look at how we can use other tasks to execute our tasks!

## Task Outputs

```yaml
tasks:
- task: Echo
  name: A
  message: Another message for the console
- task: Echo
  name: B
  message: '{{ Echo.A.outputs.message }}'

jobs:
  job-b:
    tasks:
    - Echo.A
    - Echo.B
```

Every time a task is executed, it produces a dictionary of outputs and stores them in memory for tasks that get executed later down the chain. Therefore, subsequent tasks are able to use the outputs of previous tasks using the pattern `'{{ task_id.outputs.field }}'`. In this example, we have the Echo.B task printing the message that Echo.A outputted. Therefore, when we run job-b, we see:

```
$ mule -f path/to/mule.yaml job-b
Another message for the console
Another message for the console
```

Note this also works with dependencies as well. The only requirement for one task to read another's outputs is that the task it is referencing has already been executed.

## Conclusion

These are the key features of our yaml language. Our current list of available tasks are documented [here](tasks/README.md). Feel free to try out your new skills with some more useful tasks!

# Navigation
* [Task Documentation](tasks/README.md)
* [Home](../README.md)
