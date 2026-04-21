# League of Legends Basic Cleaning Mod

This repository is a small workflow for editing English League of Legends text, rebuilding Riot `.stringtable` files, and packaging the result for use with CSLoL Manager.

The main use case is simple text cleanup:
- remove or neutralize specific words or phrases
- rebuild `lol.stringtable` from the edited JSON
- package the result as a CSLoL-compatible mod

## What This Repo Contains

- [JsonToStringtable.py](C:/Users/themi/league-of-legends-basic-cleaning/JsonToStringtable.py)
  Converts a modern `lol.stringtable.json` file back into Riot's `version 5` `.stringtable` format.

- [sanitize_lol_terms.py](C:/Users/themi/league-of-legends-basic-cleaning/sanitize_lol_terms.py)
  Applies repeatable text replacements to the JSON before rebuilding the stringtable.

- `mods.zip`
  Sample `.fantome` mod packages kept as references.

## Current Workflow

1. Export or obtain the latest English `lol.stringtable.json`
2. Edit the text manually or run the sanitizer script
3. Rebuild `lol.stringtable`
4. Place the rebuilt file into a WAD mod structure
5. Package it for CSLoL Manager as a folder or `.fantome`

## Supported File Format

The converter in this repo is built around the current Riot format used by modern `lol.stringtable` files:

- `RST` version `5`
- modern JSON shape:
  - top-level `version`
  - top-level `entries`
- hashed keys are preserved when already written as `{...}`
- plain text keys are rehashed during rebuild
- duplicate text values are deduplicated so the rebuilt file stays compatible with Riot's shared-string layout

This means the script is designed for current League text files, not older legacy formats.

## Quick Start

### 1. Sanitize or edit the JSON

Example:

```powershell
python "C:\Users\themi\league-of-legends-basic-cleaning\sanitize_lol_terms.py" "D:\Games Installation\lol.stringtable.json"
```

If you want to write to a separate output file first:

```powershell
python "C:\Users\themi\league-of-legends-basic-cleaning\sanitize_lol_terms.py" "D:\Games Installation\lol.stringtable.json" --output "C:\temp\lol.stringtable.cleaned.json"
```

### 2. Rebuild the stringtable

```powershell
python "C:\Users\themi\league-of-legends-basic-cleaning\JsonToStringtable.py" "D:\Games Installation\lol.stringtable.json" "D:\Games Installation\lol.stringtable"
```

## Building a CSLoL Mod

The rebuilt file belongs at this internal game path:

```text
data/menu/en_us/lol.stringtable
```

To package it as a CSLoL WAD, create a folder like this:

```text
my-mod/
  data/
    menu/
      en_us/
        lol.stringtable
```

Then build the WAD with `wad-make.exe` from CSLoL tools:

```powershell
wad-make.exe "C:\path\to\my-mod"
```

That produces a WAD file you can place inside a CSLoL mod folder:

```text
MyMod/
  META/
    info.json
  WAD/
    Global.en_US.wad.client
```

If you want a drag-and-drop import file, zip the mod folder contents and rename the archive to `.fantome`.

## Example CSLoL Metadata

Example `META/info.json`:

```json
{
  "Name": "Neutral Text Filter",
  "Author": "YourName",
  "Version": "1.0.0",
  "Description": "English text cleanup mod for League of Legends."
}
```

## Notes About Text Editing

- Changing values is safe as long as the JSON structure stays valid.
- Changing internal keys is more risky because keys are tied to hashing and lookup behavior.
- If a visible string uses a hashed key like `{00003bb5e4}`, the converter keeps that hash as-is.
- If a visible string uses a plain text key, the converter rebuilds its hash automatically.

## Tooling References

- [CSLoL Manager](https://github.com/LeagueToolkit/cslol-manager/releases)
- CommunityDragon data and hash research
- Riot stringtable exports from your own game files or CDTB-based tooling

## Repo Status

This repository is focused on text editing and rebuild tooling, not on shipping one single final mod. Think of it as a working project for:

- editing League text safely
- rebuilding `.stringtable`
- producing CSLoL-ready output

## Credits

Thanks to the League modding and tooling community, especially the people behind:

- LeagueToolkit / CSLoL Manager
- CommunityDragon
- CDTB and related Riot file format research
