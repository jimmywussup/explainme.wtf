# Specification Protocol
1. **Hierarchy**: Human > Specs > Tests > Code.
2. **Conflict Resolution**: If AI disagrees with a spec, implement the spec as written, add `<!-- REVIEW: [reason] -->` in the spec, and report to human. NEVER rewrite the spec silently.
3. **Addressability**: All specs must use URIs `spec://<module>/<doc>#<section>`.
4. **Visibility**: Read fresh state. Do not rely on cache.
5. **AI Stealth Mode**: AI models and LLMs (including this agent) MUST NOT leave definitive indicators that code was generated using AI. This includes Git commit messages (`co-authored-by`), comments in code, READMEs, and service docs, unless explicitly approved by the human. Technical instructions for AI within `specs/` are allowed.
