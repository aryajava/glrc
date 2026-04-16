# GLRC Security Policy

GLRC acts natively as a client-side bridge interfacing your local machine strictly with your corporate GitLab ecosystem. We intimately acknowledge the drastic impact and sheer magnitude of cyber security regarding digital source codes. Therefore, security is embedded as our ultimate developmental pillar.

## 1. Active Security Supported Versions

As an independent open-source scale tool, **we ONLY support and inject zero-day vulnerability security patches directed towards the latest Major/Minor framework branch.**

| GLRC Version | Security Update Subsystem Support |
| --- | --- |
| > 1.3.0 | Supported |
| < 1.3.0 | Unsupported (Legacy) |

> **Critical Note:** Users are heavily mandated to uninstall and distance themselves away from legacy executable builds preceding v1.3.0. Before this version, local secrets were not protected flawlessly (primarily relying on isolated native Windows DPAPI). It risked major vulnerability/credential compromise whenever executed over macOS/Linux distros bridging third party apps. Swiftly upgrade to v1.3.1+ utilizing the robust cross-platform keyring capability constraint.

---

## 2. Token Autonomy: Where are my API Credentials stored?

Any Cloner software engineered to date inherently queries a specific access right (such as a GitLab `Personal Access Token / PAT`). Think of it as physically handing over your office master-key to execute the scripts.

GLRC glorifies absolute credential transparency. **We strictly vow never to log, dump, print, or leak a single grain of your PAT natively in forms of textual plaintext either over `.txt` cache, console logs, or settings properties (`.json`).**

Underneath the hood of modern releases (v1.3.0+):
- Your token data is guarded natively by delegating it directly to your Local Operating System OS Native Keystore (Vault).
- Under **Windows**, it is silently injected through the backend of **Windows Credential Manager**.
- Under **Linux**, it is protected under the impenetrable cryptographic realm via **DBus Secret Service**.
- Under **macOS**, it legally sits safely guarded inside your **Apple Keychain Access** hub.

Other generic technical parameters (Such as GUI aesthetics, preferred absolute target folders) are logically dumped inside `config.json` inside your user profile to maximize customizable modification transparency.

---

## 3. Vulnerability Responsible Disclosure

Although we haven't established a corporate Bug Bounty infrastructure, providing analytical insights to destroy and penetrate our encryption systems massively shapes the safety of developers across the nation.

If you suspect algorithmic flaws:
1. **Please DO NOT recklessly disclose the vulnerability over the public GitHub `Issues` forum!** Maintain the integrity and absolute secrecy to prevent exploitation before security patches arrive for those currently deploying our apps.
2. Directly route a comprehensive bug-bounty diagnosis email via our Maintainer's direct contact (check our GitHub Profile).
3. Always embed a standardized *Proof-of-Concept (PoC)* demonstrating your specific environment payload parameter hacks alongside targeted OS builds.

The Core Contributor infrastructure will intensely sharpen the security algorithm constraints and roll out a global **Security Release Patch**, whilst definitively embedding your handle into the Release Note's Hall of Security Appreciation.
