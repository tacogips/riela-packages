# project-design-and-implement-review-loop-feature-plan

Package for the `design-and-implement-review-loop-feature-plan` workflow.

```bash
rielflow workflow search feature-plan --registry default --refresh
rielflow workflow checkout project-design-and-implement-review-loop-feature-plan --project-root .rielflow --registry default --output json
rielflow workflow validate design-and-implement-review-loop-feature-plan
rielflow workflow usage design-and-implement-review-loop-feature-plan --output json
rielflow workflow run design-and-implement-review-loop-feature-plan --mock-scenario .rielflow/workflows/design-and-implement-review-loop-feature-plan/mock-scenario.json --output json
```

Registry URL: `https://github.com/tacogips/rielflow-packages`.
Default local checkout: `<checkout-root>/rielflow-packages`.
