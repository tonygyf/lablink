"""Create a source-only archive; never walk arbitrary user configuration directories."""
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ["README.md", "LICENSE", "CHANGELOG.md", "pyproject.toml", ".gitignore", "config.example.json", "lablink.cmd"]
DIRS = ["lablink", "tests", "scripts", "docs", ".github"]
ALLOWED = {".py", ".ps1", ".md", ".yml"}


def build():
    files = [ROOT / p for p in FILES]
    for directory in DIRS:
        files += [p for p in (ROOT / directory).rglob("*") if p.is_file() and p.suffix in ALLOWED and "__pycache__" not in p.parts]
    for p in files:
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            raise ValueError("Unexpected symlink or external file")
        data = p.read_bytes()
        for marker in (b"-----BEGIN OPENSSH PRIVATE KEY", b"-----BEGIN RSA PRIVATE KEY", b"tskey-auth-"):
            if marker in data:
                # The scanner source is allowed to name its own literal markers.
                if p != Path(__file__).resolve():
                    raise ValueError(f"Potential secret in {p.relative_to(ROOT)}")
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    path = out / "lablink-0.1.0-source.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            z.write(p, str(Path("lablink") / p.relative_to(ROOT)))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / (path.name + ".sha256")).write_text(f"{digest}  {path.name}\n")
    print(path)
    print(f"{len(files)} source files; SHA256 {digest}")
    return path


if __name__ == "__main__":
    build()
