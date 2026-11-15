# Captures from real machines

Recordings of what a machine shows about the hypervisor under it, made by [`tools/lab-capture`](../../../../tools/lab-capture) and stored as captured. Each folder's `SOURCE.txt` says when and where it was made and what was masked.

| Folder | Machine | Made by |
| --- | --- | --- |
| `runner-azure-arm64` | A GitHub-hosted Arm runner: an Azure virtual machine on a Cobalt 100 processor | The Capture workflow, 2026-11-15 |
| `runner-azure-x64` | A GitHub-hosted x86 runner: an Azure virtual machine on an AMD EPYC processor | The Capture workflow, 2026-11-15 |

Questions in the content that quote one of these say so, and name the folder in their topic's notes. To make another, start the Capture workflow from the Actions tab (or `gh workflow run capture.yml`) and download the run's artifacts.
