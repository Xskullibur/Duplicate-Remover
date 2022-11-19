# Duplicate File Remover
This is a simple Python script to remove duplicate files by its MD5 hash value

## Description
This script includes two functions:
1. Remove duplicate files by its MD5 hash value
2. Remove Invalid files with a file size of 0 Bytes

## Getting Started
### Dependencies
- Python 3.10

### Usage
```commandline
main.py --directory DIRECTORY [--invalid-files] [--recursive] [--confirmation]
```

| Flags                     | Description                                  |
|---------------------------|----------------------------------------------|
| `-directory` or `-d`      | Target directory to look for duplicate files |
| `--invalid-files` or `-i` | Enable removal of 'invalid' files            |
| `--recursive` or `-r`     | Recursively look for duplicate files         |
| `-confirmation` or `-c`   | Prompts confirmation for deletion of file    |

## Acknowledgements
- [Customizable Progress Bar](https://stackoverflow.com/a/34325723/20549570)