# Greeting Container

Workflow package example with a single native container node.

The workflow builds a small Node.js container, picks one greeting from a fixed
set, and writes the greeting plus current datetime to the rielflow mailbox
output.

The workflow defaults to the `docker` runner.

Run as a temporary workflow from the registry:

```bash
rielflow workflow run greeting-container --from-registry --registry default --variables '{"workflowInput":{"name":"Taco","greetingIndex":1,"timezone":"Asia/Tokyo"}}'
```
