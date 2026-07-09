# Aplikasi Internet Data Monitor

## Install

```sh
pip install -r requirements.txt
```

---

## Build

### Proses Build .exe

```sh
pyinstaller --noconsole --onefile main.py
```

Build dengan icon:

```sh
pyinstaller --noconsole --onefile --icon=icon.ico main.py
```

Build dengan config app.spec

```sh
pyinstaller app.spec
```

---
