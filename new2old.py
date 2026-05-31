#!/data/data/com.termux/files/usr/bin/python
"""
Convert pyproject.toml → setup.py, preserving setup.cfg & MANIFEST.in.
Handles C-extensions: setuptools, scikit-build-core, meson-python.
Usage:
    python convert_pyproject_to_setup.py [--force] [pyproject.toml path]
"""

import configparser
import os
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def safe_read_file(path: Path) -> Optional[str]:
    return path.read_text(encoding="utf-8") if path.exists() else None


def extract_metadata(toml_data: dict) -> Dict[str, Any]:
    project = toml_data.get("project", {})
    build_system = toml_data.get("build-system", {})
    tool = toml_data.get("tool", {})
    metadata = {
        "name": project.get("name", ""),
        "version": project.get("version", "0.0.0"),
        "description": project.get("description", ""),
        "readme": project.get("readme", {}),
        "requires_python": project.get("requires-python", ""),
        "license": project.get("license", {}),
        "authors": project.get("authors", []),
        "maintainers": project.get("maintainers", []),
        "keywords": project.get("keywords", []),
        "classifiers": project.get("classifiers", []),
        "urls": project.get("urls", {}),
        "scripts": project.get("scripts", {}),
        "entry_points": project.get("entry-points", {}),
        "dependencies": project.get("dependencies", []),
        "optional_dependencies": project.get("optional-dependencies", {}),
        "include_package_data": project.get("include-package-data", False),
        "build_backend": build_system.get("build-backend", ""),
        "tool": tool,
    }
    if isinstance(metadata["license"], dict):
        metadata["license"] = metadata["license"].get("text", "")
    return metadata


def parse_setup_cfg(setup_cfg_text: str) -> Dict[str, List[str]]:
    """Parse setup.cfg sections used by setup.py generation."""
    if not setup_cfg_text:
        return {}
    cp = configparser.ConfigParser()
    try:
        cp.read_string(setup_cfg_text)
    except configparser.Error:
        return {}
    result = {}
    if "options.packages.find" in cp:
        result["packages.find"] = dict(cp.items("options.packages.find"))
    if "options.package_data" in cp:
        result["package_data"] = dict(cp.items("options.package_data"))
    if "options.data_files" in cp:
        result["data_files"] = dict(cp.items("options.data_files"))
    if "options.extras_require" in cp:
        result["extras_require"] = dict(cp.items("options.extras_require"))
    if "options.entry_points" in cp:
        result["entry_points"] = dict(cp.items("options.entry_points"))
    if "options.scripts" in cp:
        result["scripts"] = dict(cp.items("options.scripts"))
    # Handle [options] sections
    if "options" in cp:
        result["options"] = dict(cp.items("options"))
    return result


def has_c_extension(tool: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Detect C-extension build method.
    Returns (has_cext, method_name)
    """
    # 1. setuptools + ext_modules
    setuptools_tool = tool.get("setuptools", {})
    if setuptools_tool.get("ext-modules"):
        return True, "setuptools"
    # 2. scikit-build-core
    if "scikit-build" in tool or "scikit-build-core" in tool:
        return True, "scikit-build"
    # 3. meson-python
    if "meson-python" in tool or "build-system" in tool.get("requires", []):
        build_requires = tool.get("build-system", {}).get("requires", [])
        if any("meson-python" in r for r in build_requires):
            return True, "meson"
    # 4. CMake via setuptools or scikit-build
    if "cmake" in str(tool).lower():
        return True, "cmake"
    return False, ""


def generate_setup_py(
    metadata: Dict[str, Any],
    setup_cfg_text: Optional[str],
    manifest_text: Optional[str],
    force: bool = False,
) -> str:
    # Parse setup.cfg if present
    cfg = parse_setup_cfg(setup_cfg_text)
    # Detect C-extension method
    has_cext, cext_method = has_c_extension(metadata["tool"])
    # Extract metadata fields
    name = metadata["name"]
    version = metadata["version"]
    desc = metadata["description"].replace('"', '\\"')
    readme = metadata["readme"]
    requires_python = metadata["requires_python"] or ""
    license_ = metadata["license"] or ""
    authors = metadata["authors"]
    maintainers = metadata["maintainers"]
    keywords = metadata["keywords"]
    classifiers = metadata["classifiers"]
    urls = metadata["urls"]
    scripts = metadata["scripts"]
    entry_points = metadata["entry_points"]
    dependencies = metadata["dependencies"]
    optional_deps = metadata["optional_dependencies"]
    include_package_data = str(metadata["include_package_data"]).lower()
    build_backend = metadata["build_backend"]
    # Prepare install_requires
    install_requires = ",\n        ".join(f'"{d}"' for d in dependencies) if dependencies else ""
    install_requires_str = f"[\n        {install_requires}\n    ]" if install_requires else "[]"
    # Prepare extras_require
    extras_parts = []
    for extra, deps in optional_deps.items():
        deps_str = ", ".join(f'"{d}"' for d in deps)
        extras_parts.append(f'    "{extra}": [{deps_str}],')
    extras_str = "{\n" + "\n".join(extras_parts) + "\n    }" if extras_parts else "{}"
    # Prepare entry_points
    entry_parts = []
    for group, points in (entry_points or {}).items():
        entries = "\n".join(f'        "{k} = {v}"' for k, v in points.items())
        entry_parts.append(f'    "{group}": [\n{entries}\n    ],')
    entry_str = "{\n" + "\n".join(entry_parts) + "\n    }" if entry_parts else "{}"
    # Prepare scripts
    script_items = []
    for k, v in (scripts or {}).items():
        script_items.append(f'        "{k} = {v}"')
    scripts_str = "[\n" + "\n".join(script_items) + "\n    ]" if script_items else "[]"
    # Prepare classifiers
    class_str = ",\n        ".join(f'"{c}"' for c in classifiers) if classifiers else ""
    classifiers_str = f"[\n        {class_str}\n    ]" if class_str else "[]"
    # Prepare keywords
    keywords_str = ", ".join(f'"{k}"' for k in keywords) if keywords else "[]"

    # Prepare author/maintainer
    def format_authors(auths):
        return ", ".join(f"'{a.get('name', '')} <{a.get('email', '')}>'" for a in auths if a.get("name"))

    author_str = format_authors(authors)
    maintainer_str = format_authors(maintainers)
    # Readme handling
    long_desc = ""
    long_desc_type = "text/markdown"
    if isinstance(readme, dict):
        file = readme.get("file", "")
        if file and Path(file).exists():
            long_desc = Path(file).read_text(encoding="utf-8")
            long_desc_type = readme.get("content-type", "text/markdown")
        else:
            long_desc = readme.get("text", "")
            long_desc_type = readme.get("content-type", "text/plain")
    elif isinstance(readme, str):
        if Path(readme).exists():
            long_desc = Path(readme).read_text(encoding="utf-8")
            if readme.endswith(".md"):
                long_desc_type = "text/markdown"
            elif readme.endswith(".rst"):
                long_desc_type = "text/x-rst"
            else:
                long_desc_type = "text/plain"
    # Build package configuration
    packages_section = "find_packages()"
    if cfg.get("packages.find"):
        kwargs = cfg["packages.find"]
        exclude = kwargs.get("exclude", "").split(",") if kwargs.get("exclude") else []
        exclude = [e.strip() for e in exclude if e.strip()]
        if exclude:
            packages_section = f"find_packages(exclude={exclude})"
    # Build package_data/data_files from setup.cfg
    package_data_str = ""
    if "package_data" in cfg:
        pkg_data_lines = []
        for pkg, files in cfg["package_data"].items():
            files_list = [f.strip() for f in files.split(",") if f.strip()]
            pkg_data_lines.append(f'    "{pkg}": {files_list}')
        package_data_str = "    package_data={\n" + ",\n".join(pkg_data_lines) + "\n    },\n"
    data_files_str = ""
    if "data_files" in cfg:
        df_lines = []
        for target, files in cfg["data_files"].items():
            files_list = [f.strip() for f in files.split(",") if f.strip()]
            df_lines.append(f'        ("{target}", {files_list})')
        data_files_str = "    data_files=[\n" + ",\n".join(df_lines) + "\n    ],\n"
    # C-extension generation
    cext_imports = ""
    cext_extension = ""
    cext_build = ""
    if has_cext:
        if cext_method == "setuptools":
            # Example: tool.setuptools.ext-modules = [{name = "mymodule", sources = ["src/module.c"]}]
            ext_modules = metadata["tool"].get("setuptools", {}).get("ext-modules", [])
            ext_list = []
            for ext in ext_modules:
                name = ext.get("name", "")
                sources = ext.get("sources", [])
                if name:
                    sources_str = ", ".join(f'"{s}"' for s in sources)
                    ext_list.append(f'    Extension("{name}", sources=[{sources_str}]),')
            cext_extension = "from setuptools import Extension\n\n" + "\n".join(ext_list) if ext_list else ""
            cext_imports = "from setuptools import Extension\n"
            cext_build = (
                f"    ext_modules=[{', '.join([f'Extension("{e.get('name', '')}", sources={e.get('sources', [])})' for e in ext_modules])}],\n"
                if ext_modules
                else ""
            )
        elif cext_method == "scikit-build":
            cext_imports = "from skbuild import setup\n"
            cext_build = (
                "    cmake_args=[\n        # '-DCMAKE_BUILD_TYPE=Debug',\n    ],\n    # cmake_install_dir='src',\n"
            )
        elif cext_method == "meson":
            cext_imports = "from setuptools import setup\n"
            cext_build = "    # meson-python backend handles C/C++ build\n"
    # Main setup.py template
    setup_py = f'''#!/usr/bin/env python3
"""
Auto-generated setup.py from pyproject.toml.
Preserves setup.cfg and MANIFEST.in.
C-extension support: {cext_method or "none"}
"""
import os
{cext_imports}from setuptools import setup, find_packages
# Read long_description
long_description = """{long_desc}"""
long_description_content_type = "{long_desc_type}"
# Read MANIFEST.in if exists
if os.path.exists("MANIFEST.in"):
    with open("MANIFEST.in", "r") as f:
        manifest_content = f.read()
else:
    manifest_content = ""
# Main setup
setup(
    name="{name}",
    version="{version}",
    description="{desc}",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author="{author_str}",
    author_email="",
    maintainer="{maintainer_str}",
    maintainer_email="",
    license="{license_}",
    url="{list(urls.values())[0] if urls else ""}",
    keywords={keywords_str},
    packages={packages_section},
    include_package_data={include_package_data},
    python_requires="{requires_python}",
    install_requires={install_requires_str},
    extras_require={extras_str},
    entry_points={entry_str},
    scripts={scripts_str},
    classifiers={classifiers_str},
{package_data_str}{data_files_str}{cext_build}
)
'''
    return setup_py


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert pyproject.toml → setup.py (preserving setup.cfg & MANIFEST.in)"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing setup.py")
    parser.add_argument(
        "toml_path", nargs="?", default="pyproject.toml", help="Path to pyproject.toml (default: ./pyproject.toml)"
    )
    args = parser.parse_args()
    toml_path = Path(args.toml_path).resolve()
    if not toml_path.exists():
        print(f"❌ Error: {toml_path} not found.")
        sys.exit(1)
    # Load pyproject.toml
    print(f"📂 Loading {toml_path}...")
    toml_data = load_toml(toml_path)
    # Extract metadata
    metadata = extract_metadata(toml_data)
    # Check for existing files
    setup_cfg_text = safe_read_file(Path("setup.cfg"))
    manifest_text = safe_read_file(Path("MANIFEST.in"))
    # Check if setup.py exists
    setup_py_path = Path("setup.py")
    if setup_py_path.exists() and not args.force:
        print(f"⚠️  {setup_py_path} already exists. Use --force to overwrite.")
        sys.exit(0)
    # Generate setup.py
    setup_py_content = generate_setup_py(metadata, setup_cfg_text, manifest_text, args.force)
    # Write setup.py
    setup_py_path.write_text(setup_py_content, encoding="utf-8")
    print(f"✅ Generated {setup_py_path}")
    # Summary
    has_cext, cext_method = has_c_extension(metadata["tool"])
    print("\n--- Conversion Summary ---")
    print(f"Project: {metadata['name']} v{metadata['version']}")
    print(f"Dependencies: {len(metadata['dependencies'])}")
    print(f"Optional deps: {len(metadata['optional_dependencies'])}")
    print(f"C-extensions: {cext_method or 'none'}")
    if setup_cfg_text:
        print("✅ Preserved: setup.cfg")
    if manifest_text:
        print("✅ Preserved: MANIFEST.in")


if __name__ == "__main__":
    main()
