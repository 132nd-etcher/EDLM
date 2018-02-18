# coding=utf-8
"""
Replaces include directive with the actual markdown content
"""

from pathlib import Path

import elib

from . import Context


class Inclusion:
    sub_context: Context
    include_str: str
    markdown_source: Path
    new_index: Path


def _process_include(ctx: Context, inclusion: Inclusion):
    from . import process_markdown
    from ..._get_includes import get_includes
    inclusion.sub_context.markdown_text = inclusion.markdown_source.read_text(encoding='utf8')
    inclusion.sub_context.index_file = inclusion.new_index
    inclusion.sub_context.includes = []
    get_includes(inclusion.sub_context)
    process_markdown(inclusion.sub_context)
    ctx.markdown_text = ctx.markdown_text.replace(inclusion.include_str, inclusion.sub_context.markdown_text)
    if inclusion.sub_context.latex_refs:
        refs = set(inclusion.sub_context.latex_refs)
        refs.update(ctx.latex_refs)
        ctx.latex_refs = list(refs)


def _process_local_include(ctx: Context, inclusion: Inclusion):
    inclusion.include_str = f'//include "{inclusion.new_index.relative_to(ctx.source_folder)}"'
    inclusion.markdown_source = Path(ctx.source_folder, inclusion.new_index)
    ctx.images_used.update(inclusion.sub_context.images_used)
    _process_include(ctx, inclusion)


def _process_external_include(ctx: Context, inclusion: Inclusion):
    inclusion.include_str = f'//include "{inclusion.new_index.relative_to(ctx.source_folder.parent)}"'
    inclusion.markdown_source = Path(inclusion.new_index, 'index.md')
    inclusion.sub_context.source_folder = inclusion.new_index
    _process_include(ctx, inclusion)


def _get_unprocessed_includes(ctx: Context):
    for line_nr, line in enumerate(ctx.markdown_text.split('\n')):
        if '//include' in line:
            ctx.unprocessed_includes.append(f'line {line_nr+1:05d}: {line}')


def process_includes(ctx: Context):
    """
    Replaces include directive with the actual markdown content

    Args:
        ctx: Context
    """
    ctx.unprocessed_includes = []
    for include in ctx.includes:
        inclusion = Inclusion()
        inclusion.sub_context = ctx.get_sub_context()
        inclusion.new_index = include
        if include.is_file():
            _process_local_include(ctx, inclusion)
        elif include.is_dir():
            _process_external_include(ctx, inclusion)

    _get_unprocessed_includes(ctx)
    if ctx.unprocessed_includes:
        ctx.warning(f'there are unprocessed "//include" directives:\n{elib.pretty_format(ctx.unprocessed_includes)}')
