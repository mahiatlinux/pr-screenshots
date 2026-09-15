# Native verification

Repair SHA: `e84f15b4de5ba7766ca1637c0aa3df9fabdb71e3`.

Policy, sandbox and permission suites:

| Platform | Passed | Skipped | Failed/errors |
| --- | ---: | ---: | ---: |
| macOS 15 | 2,077 | 0 | 0 |
| Windows 2022 | 2,075 | 2 | 0 |
| Ubuntu 24.04 | 2,076 | 1 | 0 |

[Native test run](https://github.com/mahiatlinux/unsloth/actions/runs/35033584152). The XML files preserve individual results.

[Native browser run](https://github.com/mahiatlinux/unsloth/actions/runs/35033584870). Two independent macOS 15 VMs install/build the exact base and repaired Studio. Both run the actual OpenSSH/Paramiko experiment, then restore the results through authenticated chat history for the same UI scene. Before and after screenshots and metadata are included. All three composites were manually inspected.

- Google Chrome 152.0.7977.83: 1280x900.
- Microsoft Edge 152.0.4191.66: 1280x900.
- Native Safari 26.6.1: 1280x948.

The top/bottom composites crop only empty space beneath the expanded tool card. This evidence does not claim model inference.
