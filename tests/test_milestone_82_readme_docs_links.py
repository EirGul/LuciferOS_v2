from pathlib import Path


def test_readme_links_to_manifest_and_runtime_docs():
    readme = Path('README.md').read_text(encoding='utf-8')

    assert 'docs/luciferos_manifest.md' in readme
    assert 'docs/runtime_modes.md' in readme
    assert 'LuciferOS Manifest' in readme
    assert 'Runtime Modes' in readme
