# lol-game-data-snapshot

Current League of Legends LCU JSON snapshot generated from Riot client manifests.

`main` is the latest snapshot. Use Git commit references for historical reads.

The repository stores JSON only. Audio files, image files, WAD files, and GAME resources are not committed.

## Layout

Files mirror the LCU plugin path `plugins/rcp-be-lol-game-data/global/{language}/v1/...`:

```text
global/{language}/v1/{entry}
```

- `{language}`: `default` (en_US) or `zh_CN`
- `metadata.json` (repository root): snapshot manifest with `gameVersion`, `generatedAt`, `region`, `lcuManifestId`, and the size + sha256 of every committed file

## Raw URLs

URL pattern:

```text
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/global/{language}/v1/{entry}
```

Available entries per language:

| Entry | Description |
| --- | --- |
| `champion-summary.json` | All champions with id, name, roles (index for `champions/{id}.json`) |
| `champions/{id}.json` | Full champion detail: skins, spells, passive, lore |
| `champion-rune-recommendations.json` | Recommended rune pages per champion (`default` only) |
| `championperkstylemap.json` | Champion to perk style mapping (`default` only) |
| `items.json` | Items |
| `maps.json` | Maps |
| `summoner-spells.json` | Summoner spells |
| `perks.json` | Runes (perks) |
| `perkstyles.json` | Rune styles |
| `queues.json` | Queues |
| `game-mode-mutators.json` | Game mode mutators |
| `objectives.json` | Objectives |
| `skins.json` | All skins |
| `skinlines.json` | Skin lines |
| `universes.json` | Universes |

`{id}` in `champions/{id}.json` is the numeric champion id from `champion-summary.json`, e.g. `champions/1.json` for Annie.

Snapshot manifest:

```text
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/metadata.json
```

Examples:

```text
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/global/default/v1/champion-summary.json
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/global/zh_CN/v1/items.json
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/global/default/v1/champions/1.json
```

## How to access

Fetch with any HTTP client, no authentication required:

```bash
curl -fsSL https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/main/global/zh_CN/v1/champion-summary.json
```

To detect updates, poll `metadata.json` and compare `gameVersion` / `lcuManifestId` / `generatedAt`; per-file `sha256` values allow integrity checks and change detection without downloading data files.

### CDN mirror

jsDelivr mirrors the repository and adds CDN caching:

```text
https://cdn.jsdelivr.net/gh/Virace/lol-game-data-snapshot@main/global/{language}/v1/{entry}
```

Note that jsDelivr caches `@main` for a while; use a commit reference for guaranteed-fresh reads.

### Historical versions

Every update is a Git commit (message contains the game version). Replace `main` with a commit SHA to pin a snapshot:

```text
https://raw.githubusercontent.com/Virace/lol-game-data-snapshot/{commit-sha}/global/default/v1/items.json
https://cdn.jsdelivr.net/gh/Virace/lol-game-data-snapshot@{commit-sha}/global/default/v1/items.json
```

Browse the commit history of `metadata.json` to find the snapshot for a given game version.
