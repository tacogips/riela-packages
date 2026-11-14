# Release Note Node Add-on

Declarative node add-on package for generating release-note worker nodes.

Install:

```bash
riela package install release-note-node-addon
```

Use from a workflow node:

```json
{
  "addon": {
    "ref": "examples/release-note@1",
    "inputs": {
      "topic": "package registry support"
    }
  }
}
```

