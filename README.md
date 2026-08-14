# Image & PDF Toolkit

A simple, fast, offline desktop app for common image and PDF tasks — built with
PySide6 (Qt for Python).

## Features

- **Image Resizer** — compress an image down to a target file size (KB), with
  a maximum-quality cap
- **PNG → JPG** — convert images to JPG in one click
- **JPG → PDF** — combine one or more images into a single PDF
- **PDF → JPG** — export every page of a PDF as a high-quality JPG
- **Lock PDF** — password-protect a PDF
- **Unlock PDF** — remove a PDF's password

Everything runs locally — no internet connection or account required. Output
files are saved to `Desktop\Image & PDF Toolkit`.

## Running from source

Requires Python 3.11+.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Building the Windows installer

Building a distributable `Setup.exe` additionally requires
[PyInstaller](https://pyinstaller.org) and [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bash
pip install pyinstaller
pyinstaller --name "ImagePDFToolkit" --onefile --windowed --icon assets/icons/app.ico --add-data "assets;assets" --add-data "VERSION;." app.py
```

Then download the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
into `installer/downloads/vc_redist.x64.exe`, and compile the installer:

```bash
ISCC installer\setup.iss
```

The resulting `dist\ImagePDFToolkit-Setup.exe` is a self-contained installer
that bundles the app and installs the VC++ Redistributable only if it isn't
already present on the target machine.

## Project structure

```
app.py                  Entry point
version.py               Reads VERSION for use in the app
ui/                      Windows, pages, shared widgets, styling
tools/                    Image/PDF processing logic
assets/                   App icon, tool icons, bundled font
installer/setup.iss       Inno Setup installer script
```

## Branches & versioning

- `dev` — active development. Day-to-day changes land here first.
- `master` — production. Only merge `dev` into `master` once a change has
  been verified working; this is what the installer is built from.

`VERSION` at the repo root is the single source of truth for the app's
version number — both the app itself (window title, sidebar footer) and the
installer read it from there, so it only needs to be bumped in one place.
Bump it (following [semver](https://semver.org)) whenever you merge a
meaningful change into `master`.

## License

MIT — see [LICENSE](LICENSE). © 2026 Rahul Swargam.
