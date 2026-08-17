# Vimm's Lair Downloader

Download and extract files from [Vimm's Lair](https://vimm.net/).

## Usage

1. Put vault URLs in `links.txt` (one per line):

```text
https://vimm.net/vault/15610
https://vimm.net/vault/15599
```

2. Download:

```bash
./download.sh
```

Files are saved to `out/`.

3. Extract (unpacks into `out/` and **deletes** the zip/7z):

```bash
./extract.sh
```

To extract **without** deleting the archives:

```bash
./extract.sh --no-delete
```

## Layout

```text
links.txt        # vault URLs
download.sh      # download everything
extract.sh       # extract everything
out/             # downloads + extracted files
scripts/         # Python code
requirements.txt
```

## Requirements

- Python 3.x

On first run the scripts create `.venv`, install dependencies, and create `out/`.
