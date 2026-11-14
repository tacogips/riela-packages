# Greeting Container

Workflow package example with a single native container node.

The workflow builds a small Node.js container, picks one greeting from a fixed
set, and emits the greeting plus current datetime as Riela node output.

The workflow defaults to the `docker` runner.

Run as a temporary workflow from the registry:

```bash
riela workflow run greeting-container --from-registry --registry default --variables '{"workflowInput":{"name":"Taco","greetingIndex":1,"timezone":"Asia/Tokyo"}}'
```
