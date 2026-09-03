# Lab 11: Poisoned pipeline execution (PPE)

The default Azure Pipelines file lives in-repo and PR builds can use it with secrets available. A contributor who edits the YAML can run attacker-controlled steps.

**OWASP Top 10:2025:** [A03 Software Supply Chain Failures](https://owasp.org/Top10/2025/) / [A08 Software or Data Integrity Failures](https://owasp.org/Top10/2025/)

**Code:** compare these two files (read comments at the top of each):

- Unsafe (default path ADO picks up): [`../../azure-pipelines.yml`](../../azure-pipelines.yml)
- Hardened shape: [`../../pipelines/azure-pipelines.hardened.yml`](../../pipelines/azure-pipelines.hardened.yml)

## Exploit (read-only lab)

1. Open `azure-pipelines.yml`. Note intentionally bad patterns:

   - Pipeline YAML editable by PR authors
   - Secret variable group available to PR validation jobs
   - `persistCredentials: true` on checkout
   - Inline script that could echo / exfiltrate secrets

2. Open `pipelines/azure-pipelines.hardened.yml`. Note the safer shape:

   - `extends` a template from a protected repo/branch PRs cannot edit
   - Secrets only on non-PR (main) builds
   - No `persistCredentials` on PR checkout
   - Deploy gated; build job without production service connection

Do not wire either file to real credentials. This lab is documentation comparison, not a live Azure DevOps attack.

## Fix

- Lock pipeline steps in a protected template repo; app PRs only pass parameters.
- Do not expose secret groups to PR builds from forks or untrusted branches.
- Separate build and deploy identities; gate deploy with environments and approvals.

Read the header comments (`VULN`-style notes) in both YAML files.
