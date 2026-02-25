### Contributing to OGA Local Service Atlas Tracker

Thank you for your interest in contributing to the OGA Local Service Atlas Tracker. This project is part of the OpenGov Africa (OGA) ecosystem and is built as long-term civic infrastructure. Contributions are expected to prioritize auditability, data integrity, documentation, and sustainability over speed or short-term demos.

This repository is scaffold-first. Early contributors are expected to help define foundations rather than assume existing infrastructure.

---

### Who Can Contribute

This project welcomes contributors of all experience levels, including:
- New open-source contributors
- Civic technologists
- Researchers and data practitioners
- Developers contributing through programs such as GSoC, Outreachy, MLH, or internships

All contributors are expected to follow the ownership, review, and documentation standards defined below.

---

### How Work Is Organized

All work is coordinated publicly through GitHub.

- **GitHub Issues** are the source of truth for tasks and ownership.
- **GitHub Discussions** are used for architectural questions, planning, and coordination.
- **Pull Requests** represent concrete implementation work and must always reference an Issue.

Before starting work:
1. Read the README and roadmap.
2. Browse open Issues and labels.
3. Claim an Issue by commenting clearly that you are taking ownership.

Each Issue must have **one primary owner**.

---

### Individual Ownership Model

This project follows an **individual-ownership, collaborative-development** model across all phases of work.

Collaboration through discussion, review, and feedback is encouraged and expected. However, all implemented work must have clearly attributable ownership.

- One Issue → one owner
- One Pull Request → one author
- One deliverable → one accountable contributor

Collaboration should improve quality, not dilute accountability.

---

### Contributors & Roles

This project follows an individual-ownership, collaborative-development model across all phases of work and maintains explicit attribution for all contributors. Contributors are encouraged to collaborate through discussion, reviews, and coordination at every stage of the project. However, all implemented work must have clearly attributable ownership.

Each contributor is credited with the specific components, tasks, or deliverables they owned or led. Participation, discussion, or review alone does not imply ownership.

| Contributor | Role / Focus Area | Owned Deliverables |
|------------|------------------|--------------------|
| Name / GitHub | Backend, Frontend, Data, Infra, Research | Clearly scoped features, services, or setup tasks |

This table must be kept up to date as the project evolves, from Phase 0 through final delivery. Phase-level credit is insufficient on its own; ownership must always be traceable to concrete deliverables, from initial scaffolding (Phase 0) through final handover.

**Clarification on Collaboration and Ownership (All Phases)**

From Phase 0 through the final phase, contributors may not jointly claim the same implementation output unless responsibilities are explicitly separated and documented. Collaboration should strengthen implementation quality, not dilute accountability.

---

### Pull Request Requirements

Every Pull Request must:
- Reference a GitHub Issue with a clearly identified owner
- Contain only work owned by the PR author
- Be small, focused, and reviewable
- Include relevant documentation updates
- Pass all CI checks

Reviewers may suggest changes, but the PR author must apply them. Reviewers must not push commits directly to another contributor’s branch.

---

### Definition of Done

A task or feature is considered complete only when all of the following are satisfied:

1. Code is clean, readable, and compliant with project linting and formatting rules.
2. Appropriate unit and/or integration tests are included and CI passes.
3. Relevant documentation is updated (README, ARCHITECTURE, API docs where applicable).
4. Database migrations are provided and reviewed if schema changes are involved.
5. The Pull Request has received at least one peer review and maintainer approval.

Work that does not meet all criteria will not be merged.

---

### Data and Integrity Rules

Because this is a civic data platform, the following are strict requirements:

- All spatial data must use GeoJSON.
- No inferred, fabricated, or guessed data is allowed.
- All records must have clear provenance (source, timestamp, actor).
- Citizen-submitted data must be treated as unverified until reviewed.
- Schema changes require written justification.

Code that compromises data integrity, provenance, or auditability will not be accepted.

---

### Relationship to Tech Programs, Hackathons & Internships

This project may be developed in part through tech programs. If you are contributing through GSoC, MLH, Outreachy, or similar programs, please review the OGA project standard and roadmap:

- Project standard: https://github.com/OpenGovAfrica/gsoc/blob/main/docs/project-standard.md  
- Roadmap: https://github.com/OpenGovAfrica/gsoc/issues/20  

If these links become obsolete, please raise an Issue to update them.

Contributors participating through programs are expected to:
- Build reusable, well-documented components
- Respect long-term maintenance needs
- Treat programs as an entry point, not a finish line

The roadmap and contribution guidelines are designed for continuity beyond any single program.

---

### GSoC Compatibility Note

GSoC compatibility: Contributors may collaborate through discussion and peer review, but all submitted work must have clear individual ownership and be attributable to a single contributor for evaluation.

Shared ownership of identical deliverables is not permitted.

---

### Maintainer Enforcement Guidelines

These guidelines apply from Phase 0 through final project delivery.

Maintainers are responsible for ensuring clear ownership and accountability throughout the project lifecycle. When reviewing work, maintainers should verify that:

1. Every pull request has a clearly identifiable primary owner.
2. Each deliverable, regardless of phase, is attributable to a specific contributor.
3. The README “Contributors & Roles” section reflects actual implementation ownership, not participation alone.
4. Multiple contributors are not credited for the same deliverable unless roles and responsibilities are explicitly differentiated.
5. Collaboration is demonstrated through reviews, discussions, and coordination, not shared ownership of identical outputs.

If ownership is unclear at any stage, maintainers should request clarification or restructuring before merging.

Clear ownership is required for all phases to ensure sustainability, accountability, and long-term project health.

---

## Development Setup & Technical Guidelines

For detailed setup instructions, local development workflow, linting rules, and testing standards, please refer to our:

[**docs/contributor.md**](https://github.com/OpenGovAfrica/oga-local-service-atlas/blob/main/docs/CONTRIBUTING.md)

All contributors must follow both the governance model in this document and the technical standards present in the docs/contributor.md.

---

### Getting Help

If anything is unclear:
- Ask questions early in GitHub Discussions
- Reference relevant documentation in `docs/`
- Propose improvements via Issues

If it is not written down, it does not exist. Documentation is a core contribution.
