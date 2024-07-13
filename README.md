# vaiko

A minimalistic voice-to-keystroke detector.

![Sample Image](docs/sample.jpg)

## Usage

```powershell
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run vaiko
py vaiko
```

Launching the program for the first time generates an empty `words.yaml` file in the `vaiko` directory. Populate the file with simple `word: "<keystroke>"` entries to specify which words to look out for and their corresponding input to invoke. 

Only mouse and keyboard inputs are supported, with corresponding input codes based on those [pynput](https://pypi.org/project/pynput/) support. Note that only **one input at a time per word** is currently supported. Moreover, phrase detection is not supported.