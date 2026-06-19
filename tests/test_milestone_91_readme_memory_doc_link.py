from pathlib import Path


def test_readme_links_to_memory_architecture_doc():
    readme = Path('README.md').read_text(encoding='utf-8')

    assert 'docs/memory_architecture.md' in readme
    assert 'Memory Architecture' in readme
    assert 'memory architecture document' in readme.lower()
