# Security Policy

MediLedger Nexus is a decentralized health data platform that combines encrypted health vaults, Hedera services and smart contracts, zk-SNARKs, and AI-assisted diagnostics. Because the platform may process highly sensitive health information and blockchain credentials, security reports are handled confidentially and with priority.

This policy describes how to report vulnerabilities, the platform threat model, and the security practices expected for development and deployment.

## Supported Versions

Security fixes are applied to the default branch and to the most recent tagged release when practical. Deployments should use the latest supported release and current dependency lock files.

Older releases may not receive security fixes. Operators should upgrade before reporting a vulnerability against an unsupported version.

## Vulnerability Reporting Policy

### Private reporting

Please report suspected vulnerabilities to:

**security@mediledgernexus.com**

Do not open a public GitHub issue, discussion, pull request, or social-media post for an unpatched vulnerability. Public disclosure can expose patients, operators, and network accounts to avoidable harm.

When possible, use an email subject in this format:

`[SECURITY] <short vulnerability description>`

If the report contains sensitive evidence, request the project PGP public key before sending attachments. Do not send health records, access tokens, passwords, Hedera private keys, recovery phrases, or other production secrets. Use synthetic or redacted data and include hashes, logs, or minimal reproducible steps instead.

### What to include

A useful report should contain:

- A concise description of the vulnerability and its security impact.
- The affected component, version, commit, endpoint, contract, circuit, or dependency.
- Reproduction steps or a minimal proof of concept that does not access real patient data.
- Required permissions, configuration, network assumptions, and attack complexity.
- Any known workaround or mitigation.
- Your preferred contact details for follow-up.

If you accidentally disclose a secret, state that clearly in the subject line and do not include the secret again. Rotate or revoke it immediately when possible and contact the security team through the address above.

### Response process

The maintainers will acknowledge receipt within three business days when a reply address is available. They will triage the report, reproduce the issue in an isolated environment, coordinate remediation, and communicate material status changes. Timelines may vary with severity, exploitability, required upstream fixes, and coordinated disclosure constraints.

The project aims to coordinate public disclosure after a fix or mitigation is available. Reporters will be credited unless they request anonymity. We ask reporters to allow reasonable time for remediation and to avoid accessing, altering, retaining, or disclosing data that does not belong to them.

## Threat Model

### Security objectives

The platform is designed to protect:

- **Confidentiality:** health records, personally identifiable information, credentials, encryption keys, AI prompts, and model outputs.
- **Integrity:** health data, consent decisions, access events, zk-SNARK public inputs and proofs, smart-contract state, and diagnostic responses.
- **Availability:** authorized access to health vaults, consent workflows, emergency workflows, and audit records.
- **Accountability:** attributable changes and access events through application authentication, service logs, and Hedera consensus records.

Hedera consensus and immutability do not by themselves make off-chain data, application authorization, model output, or client devices trustworthy.

### Assets and trust boundaries

The principal assets are:

- Encrypted health data and metadata stored off-chain or in application-managed storage.
- User identities, access tokens, consent records, emergency-access records, and audit events.
- Hedera account IDs, operator private keys, transaction-signing credentials, and contract administration keys.
- zk-SNARK circuits, proving keys, verification keys, public inputs, proofs, and verifier contracts.
- AI models, prompts, retrieved context, federated-learning updates, diagnostic outputs, and provider feedback.
- Database, object-store, IPFS, Arweave, Redis, monitoring, CI/CD, and deployment credentials.

Important trust boundaries include:

1. User and provider clients to the API.
2. The API to databases, file storage, IPFS, Arweave, Redis, and external AI providers.
3. Application services to Hedera consensus, token, and smart-contract transactions.
4. Provers and clients to zk-SNARK verification circuits and verification keys.
5. Development and CI/CD systems to production deployment credentials.
6. AI services to clinical users and downstream care workflows.

### Adversaries and assumptions

The threat model considers unauthenticated internet attackers, compromised user accounts, malicious or negligent authorized users, compromised dependencies, malicious data submitters, compromised AI inputs, and attackers who obtain deployment or Hedera credentials. It also considers service outages, replayed requests, manipulated public inputs, and malicious or incorrect model outputs.

The model assumes that cryptographic libraries, the selected Hedera network, and correctly generated verification keys are trustworthy. It does not assume that client devices, external AI providers, application operators, or user-supplied data are trustworthy.

### Threats and controls

#### Health data privacy

**Threats:** unauthorized API access, broken object-level authorization, token theft, database or backup exposure, inference from metadata, insecure logs, accidental PHI disclosure to AI providers, and cross-tenant data access.

**Controls and expectations:**

- Enforce authentication, authorization, consent state, tenant boundaries, and least privilege on every data access path.
- Encrypt health data in transit and at rest; keep encryption keys outside source control and rotate them through a managed secret process.
- Validate request bodies and file types, limit uploads, and prevent path traversal and unsafe deserialization.
- Minimize PHI in logs, traces, metrics, error messages, prompts, and analytics. Redact identifiers before exporting telemetry.
- Use synthetic data in tests and development. Do not place PHI in issue reports or CI artifacts.
- Treat IPFS, Arweave, databases, backups, and third-party AI systems as separate trust domains and verify access policies for each.
- Apply retention, deletion, access-review, and incident-response procedures appropriate to the deployment and applicable law.

Encryption does not replace authorization, key management, or secure endpoint behavior. Operators remain responsible for configuring storage, backups, networking, and secrets correctly.

#### zk-SNARK validation integrity

**Threats:** forged or replayed proofs, incorrect public inputs, circuit or verifier bugs, mismatched proving and verification keys, compromised trusted setup material, missing nullifier checks, and acceptance of a proof without binding it to the intended user, record, consent, or contract state.

**Controls and expectations:**

- Treat circuits, verification keys, and verifier contracts as security-critical code and review changes independently.
- Pin the circuit, compiler, proving key, verification key, and verifier version used for each proof format.
- Validate field ranges, domain separation, statement identifiers, timestamps or epochs, record commitments, and all public inputs before verification.
- Bind proofs to the intended application context and enforce replay protection, nullifiers, expiry, and authorization checks outside the proof where required.
- Verify proofs on the server or trusted contract boundary; never accept a client-provided verification result as evidence.
- Protect trusted-setup artifacts and document their provenance. Regenerate or revoke verification material when the circuit or setup is invalidated.
- Test negative cases, malformed proofs, altered public inputs, cross-context replay, and boundary values.

A valid proof establishes only the statement encoded by the circuit and its public inputs. It does not prove that the underlying data is clinically correct, ethically collected, or safe to use for diagnosis.

#### Hedera account private keys

**Threats:** keys committed to source control or `.env` files, leaked through logs or CI output, over-privileged operator accounts, malware on deployment hosts, unauthorized transaction signing, and reused keys across environments.

**Controls and expectations:**

- Store private keys only in an approved secret manager, HSM, or equivalent protected runtime mechanism. Never hardcode, commit, print, or paste them into tickets.
- Use separate accounts and keys for local development, testnet, staging, and production. Use least-privilege accounts for each service.
- Restrict signing operations, monitor transactions, set operational limits where supported, and require approval for administrative actions.
- Keep `.env` files, wallet files, generated key files, and CI secrets out of version control and artifacts.
- Rotate or revoke compromised keys immediately, inspect recent transactions, and document the incident.
- Treat Hedera consensus records as durable. Do not submit PHI or unnecessary secrets to public topics or transactions; store only suitable commitments, references, or minimized metadata.

#### AI diagnostics and federated learning

AI output is advisory and must not be treated as an autonomous diagnosis or emergency decision. Threats include prompt injection, malicious clinical content, model hallucination, training-data poisoning, membership inference, leakage through prompts or outputs, model substitution, and unsafe reliance by users.

Use data minimization, provenance checks, model and prompt versioning, access controls, output validation, audit trails, provider review, and human clinical oversight. Federated learning reduces direct data sharing but does not eliminate poisoning, update leakage, or inference risks; secure aggregation and participant authentication should be used where supported.

### Out of scope

Unless they demonstrate a vulnerability in this project, the following are generally outside the scope of a report:

- Vulnerabilities requiring physical access to a reporter-controlled device.
- Availability issues caused solely by a Hedera network or unrelated third-party provider outage.
- Findings that disclose only intentionally public blockchain state.
- Automated scanner output without a reproducible security impact.
- Social engineering, spam, or denial-of-service testing against production systems.

## Dependency Auditing and Compliance

Dependencies, container images, smart-contract libraries, circuit tooling, and build actions are part of the security boundary. Maintainers should:

- Pin or constrain dependencies and review lock-file changes.
- Run automated software-composition analysis and vulnerability scanning in CI, including transitive dependencies.
- Monitor security advisories and apply critical fixes according to severity and exploitability.
- Generate and retain a software bill of materials (SBOM) for release artifacts where the deployment process supports it.
- Review third-party licenses and preserve required notices; reject dependencies whose terms are incompatible with the project or deployment.
- Verify release provenance, checksums, and build permissions, and keep CI tokens least-privileged.
- Test dependency upgrades, cryptographic changes, circuit changes, and contract changes before deployment.

Security practices support risk management and can assist with HIPAA, GDPR, and other applicable obligations, but this repository does not by itself certify compliance. Operators and deploying organizations are responsible for legal review, data-processing agreements, regional controls, clinical governance, breach notification, retention, and access-request procedures.

## Secure Development Expectations

- Do not commit secrets, PHI, private keys, wallet files, generated proofs, or production datasets.
- Prefer synthetic fixtures and negative security tests.
- Review authentication, authorization, cryptography, circuit, contract, and AI changes with an appropriate second reviewer.
- Run tests, static analysis, dependency scans, and secret scans before release.
- Record security-relevant changes and communicate breaking changes to operators.

For questions about this policy or to request the security contact's encryption key, email **security@mediledgernexus.com**.
