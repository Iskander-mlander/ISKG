"""Bundled project templates for ``iskg new <name>``.

Each template is a directory of plain text files (UTF-8, LF line endings;
the CLI converts to the platform's native line endings on write). Templates
are intentionally tiny — they are starting points, not frameworks.

Adding a new template: create a directory under ``iskg/scaffolds/<name>/``
and (optionally) add a ``__meta__.py`` describing the template. The CLI
picks it up automatically.
"""
