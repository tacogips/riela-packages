# Greeting Node Add-on

Executable node add-on package that installs `examples/greeting-shell@1`, a
native Bash command node template that outputs a JSON greeting.

## Install

```bash
rielflow package install greeting-node-addon
```

## Runtime

The installed executable add-on expects `bash`, `date`, and `jq` on the worker
host. `jq` is used to encode mailbox JSON safely for arbitrary string inputs.

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
