from __future__ import annotations

import argparse
import platform
import re
import subprocess
import sys
from pathlib import Path

LANG_TARGETS = {
    "en": "glrc-en",
    "id": "glrc-id",
}

ASSET_FILES = [
    "VERSION",
    "default_lang.txt",
    "assets/icons/logo.png",
    "assets/icons/logo.ico",
    "assets/fonts/MaterialIcons-Regular.ttf",
    "assets/fonts/OpenSans-Regular.ttf",
    "assets/fonts/OpenSans-Bold.ttf",
    "assets/fonts/OpenSans-Italic.ttf",
    "assets/fonts/OpenSans-Light.ttf",
    "assets/fonts/OpenSans-Medium.ttf",
]

APP_VERSION_FALLBACK = "1.0.0"
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PRODUCT_NAME = "GLRC: GitLab Repo Cloner"
COMPANY_NAME = "GLRC Project"
COPYRIGHT = "Copyright (c) 2026 GLRC Project"

LANG_VERSION_META = {
    "en": {
        "description": "GLRC: GitLab Repo Cloner (English)",
        "translation": (1033, 1200),  # en-US, Unicode codepage
        "string_table": "040904B0",
    },
    "id": {
        "description": "GLRC: GitLab Repo Cloner (Bahasa Indonesia)",
        "translation": (1057, 1200),  # id-ID, Unicode codepage
        "string_table": "042104B0",
    },
}


def run(cmd: list[str], cwd: Path) -> None:
    print("[RUN]", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def read_app_version(repo_root: Path) -> str:
    version_path = repo_root / "VERSION"
    if version_path.exists():
        value = version_path.read_text(encoding="utf-8").strip()
        if value:
            if not SEMVER_PATTERN.match(value):
                raise ValueError(
                    f"Invalid VERSION format: '{value}'. Expected semver 'x.y.z' (example: 1.2.3)."
                )
            return value
    return APP_VERSION_FALLBACK


def version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = [int(p) for p in version.split(".") if p.strip()]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])  # type: ignore[return-value]


def create_windows_version_file(repo_root: Path, app_name: str, lang: str, app_version: str) -> Path:
    meta = LANG_VERSION_META[lang]
    v1, v2, v3, v4 = version_tuple(app_version)
    translation_lcid, translation_codepage = meta["translation"]

    content = f'''# UTF-8
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=({v1}, {v2}, {v3}, {v4}),
        prodvers=({v1}, {v2}, {v3}, {v4}),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '{meta["string_table"]}',
                [
                    StringStruct('CompanyName', '{COMPANY_NAME}'),
                    StringStruct('FileDescription', '{meta["description"]}'),
                    StringStruct('FileVersion', '{app_version}'),
                    StringStruct('InternalName', '{app_name}'),
                    StringStruct('LegalCopyright', '{COPYRIGHT}'),
                    StringStruct('OriginalFilename', '{app_name}.exe'),
                    StringStruct('ProductName', '{PRODUCT_NAME}'),
                    StringStruct('ProductVersion', '{app_version}')
                ]
            )
        ]),
        VarFileInfo([
            VarStruct('Translation', [{translation_lcid}, {translation_codepage}])
        ])
    ]
)
'''

    version_file = repo_root / "build" / f"version-{app_name}.txt"
    version_file.parent.mkdir(parents=True, exist_ok=True)
    version_file.write_text(content, encoding="utf-8")
    return version_file


def generate_icon(repo_root: Path) -> None:
    print("[ICON] Generating multi-size logo.ico from logo.png...")
    run(
        [
            sys.executable,
            "scripts/generate_icon.py",
            "--source",
            "assets/icons/logo.png",
            "--target",
            "assets/icons/logo.ico",
            "--sizes",
            "16,24,32,48,64,128,256",
        ],
        repo_root,
    )


def pick_icon_file(repo_root: Path) -> Path | None:
    system = platform.system().lower()
    if system == "darwin":
        icns = repo_root / "assets" / "icons" / "logo.icns"
        if icns.exists():
            return icns

    ico = repo_root / "assets" / "icons" / "logo.ico"
    if ico.exists():
        return ico
    return None


def output_exe_path(repo_root: Path, app_name: str) -> Path:
    system = platform.system().lower()
    if system == "windows":
        return repo_root / "dist" / f"{app_name}.exe"
    return repo_root / "dist" / app_name


def cleanup_previous_artifacts(repo_root: Path, app_name: str) -> None:
    exe_path = output_exe_path(repo_root, app_name)
    spec_path = repo_root / f"{app_name}.spec"
    version_file = repo_root / "build" / f"version-{app_name}.txt"
    build_dir = repo_root / "build" / app_name

    if exe_path.exists():
        exe_path.unlink()
    if spec_path.exists():
        spec_path.unlink()
    if version_file.exists():
        version_file.unlink()
    if build_dir.exists():
        for path in sorted(build_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        build_dir.rmdir()


def refresh_windows_icon_cache() -> None:
    if platform.system().lower() != "windows":
        return

    print("[CACHE] Refreshing Windows icon cache...")
    # Best-effort refresh; may require closing running apps that lock icon files.
    commands = [
        ["powershell", "-NoProfile", "-Command", "Stop-Process -Name explorer -Force"],
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Remove-Item \"$env:LOCALAPPDATA\\IconCache.db\" -Force -ErrorAction SilentlyContinue",
        ],
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Remove-Item \"$env:LOCALAPPDATA\\Microsoft\\Windows\\Explorer\\iconcache*\" -Force -ErrorAction SilentlyContinue",
        ],
        ["powershell", "-NoProfile", "-Command", "Start-Process explorer.exe"],
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=False)
        except Exception as exc:
            print(f"[WARN] Icon cache refresh step failed: {exc}")


def build_one(repo_root: Path, lang: str, app_name: str) -> None:
    cleanup_previous_artifacts(repo_root, app_name)

    app_version = read_app_version(repo_root)

    default_lang_file = repo_root / "default_lang.txt"
    default_lang_file.write_text(lang + "\n", encoding="utf-8")

    data_sep = ";" if platform.system().lower() == "windows" else ":"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        app_name,
    ]

    icon_file = pick_icon_file(repo_root)
    if icon_file:
        cmd.extend(["--icon", str(icon_file)])

    if platform.system().lower() == "windows":
        version_file = create_windows_version_file(repo_root, app_name, lang, app_version)
        cmd.extend(["--version-file", str(version_file)])

    for asset in ASSET_FILES:
        asset_path = repo_root / asset
        if asset_path.exists():
            destination = str(Path(asset).parent).replace("\\", "/")
            cmd.extend(["--add-data", f"{asset}{data_sep}{destination}"])

    cmd.append("main.py")

    print(f"[BUILD] {app_name} (default lang: {lang}, version: {app_version})")
    run(cmd, repo_root)

    out_path = output_exe_path(repo_root, app_name)
    print(f"[DONE] {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-platform GLRC build helper")
    parser.add_argument(
        "--lang",
        choices=["all", "en", "id"],
        default="all",
        help="Language target to build",
    )
    parser.add_argument(
        "--refresh-icon-cache",
        action="store_true",
        help="Refresh Windows icon cache after build (Windows only)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    try:
        generate_icon(repo_root)

        targets = LANG_TARGETS.items() if args.lang == "all" else [(args.lang, LANG_TARGETS[args.lang])]
        for lang, app_name in targets:
            build_one(repo_root, lang, app_name)

        if args.refresh_icon_cache:
            refresh_windows_icon_cache()

        if platform.system().lower() != "windows":
            print("[NOTE] Cross-platform means run this script on each target OS. PyInstaller does not cross-compile across OS families.")

        return 0
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Command failed with exit code {exc.returncode}")
        return exc.returncode
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
