# Contribution

All you need to do to add tasks to this cli is implement a class implementing the [ITask](../mule/task/__init__.py) and drop it into an appropriate folder under the mule.task package in the project. Once the file is there, the reference name in your mule yaml file will be the full package name of the class, minus `mule.task.`.

Below is a hello world task you can try adding yourself! In order to use it in a mule.yaml, try making a `mule/task/helloworld` folder in your repo and write the following file to `mule/task/helloworld/hello.py`.

```python
from mule.task import ITask

class HelloWorld(ITask):

    def execute(self, job_context):
        print('Hello World!')
```

Once the file is added, and you pip install this project in edit mode (`pip3 install -e .`), you should be able to use this task in the following mule yaml.

```yaml
stages:
  hello:
  - task: helloworld.hello.HelloWorld
```

```
➜  mule git:(master) ✗ mule -f mule-hello-world.yaml hello
Hello World!
```

# Navigation
* [Home](../README.md)
