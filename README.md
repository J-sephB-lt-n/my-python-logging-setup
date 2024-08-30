# My Python Logging Setup

A toy codebase illustrating native python logging functionality.

To see it in action run

```bash
python main.py
```

Goals:

| Completed | Goal                                                                          | Notes                                                    |
| --------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| ✅        | unified logger formatting                                                     |                                                          |
| ✅        | dynamic logger formatting (easy to set and reset format, and done safely)     |
| ✅        | function decorator (logs function calls, inputs and outputs, runtime metrics) | Might not be aesthetic for all complex python data types |
| ❌        | class decorator (logs instantiations and method calls)                        | Haven't started this yet                                 |
| ✅        | section timer                                                                 |
| ❌        | flask/fastAPI route call logging                                              | Haven't started this yet                                 |
