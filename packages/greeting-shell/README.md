# Greeting Shell

Workflow package example with a single native Bash command node.

The workflow runs a local Bash script, picks one greeting from a fixed set, and
writes the greeting plus current datetime to the rielflow mailbox output.

Run as a temporary workflow from the registry:

```bash
rielflow workflow run greeting-shell --from-registry --registry default --variables '{"workflowInput":{"name":"Taco","greetingIndex":2,"timezone":"Asia/Tokyo"}}'
```
