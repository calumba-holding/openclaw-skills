# acong-host-cli-canary

Consumer-side smoke test skill for skill-publish-cli's M2 milestone. Proves that when another team (here, /Users/yarnb/host-cli) runs `skill-publish-cli publish <path>` from its own project root, the publish record lands in that team's workspace/publishes/ — not in skill-publish-cli's own workspace. Safe to uninstall; has no runtime behavior.

## Install

```bash
# via clawhub
clawhub install acong-host-cli-canary

# via skills.sh
npx skills add acong-tech/skill-acong-host-cli-canary
```

## Version

Current: `0.1.0`

## License

MIT-0. Published from https://github.com/acong-tech/skill-acong-host-cli-canary by [skill-publish-cli](https://github.com/acong-tech/skill-publish-cli).
