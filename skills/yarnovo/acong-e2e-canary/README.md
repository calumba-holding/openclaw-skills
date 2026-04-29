# acong-e2e-canary

Automated end-to-end test canary for skill-publish-cli. Reused on every test run with a bumped version — never manually installed. Verifies publish → inspect → delete → inspect → undelete → inspect round-trips across ClawHub, GitHub, and skills.sh. Safe to ignore as a human; safe to uninstall if accidentally installed (no real behavior).

## Install

```bash
# via clawhub
clawhub install acong-e2e-canary

# via skills.sh
npx skills add acong-tech/skill-acong-e2e-canary
```

## Version

Current: `0.20260421.1737`

## License

MIT-0. Published from https://github.com/acong-tech/skill-acong-e2e-canary by [skill-publish-cli](https://github.com/acong-tech/skill-publish-cli).
