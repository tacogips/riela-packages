# Greeting Node Add-on

Executable node add-on package that installs `examples/greeting-shell@1`, a
native Bash command node template that outputs a JSON greeting.

## Install

```bash
rielflow package install greeting-node-addon
```

Use the installed add-on from a workflow node:

```json
{
  "id": "greeting",
  "role": "worker",
  "addon": {
    "name": "examples/greeting-shell",
    "version": "1",
    "inputs": {
      "name": "Rielflow",
      "greetingIndex": "1",
      "timezone": "UTC"
    }
  }
}
```
