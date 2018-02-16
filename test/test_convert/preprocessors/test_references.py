# coding=utf-8

from edlm.convert import Context
from edlm.convert._preprocessor._references import Reference, process_references

DUMMY_REFS = {
    '//ref1': 'ref1_name, ref1_link',
    '//ref2': 'ref2_name, ref2_link',
    '//ref3': 'ref3_name, ref3_link',
}


def test_reference_class():
    name = 'name'
    link = 'link'
    raw_str = ','.join((name, link))
    abbrev = 'abbrev'
    ref = Reference(raw_str, abbrev)
    assert ref.abbrev == abbrev
    assert ref.name == name
    assert ref.link == link
    assert ref.to_latex() == f'\\href{{{link}}}{{{name}}}'
    assert ref.to_markdown() == f'[{name}]({link})'
    assert hash(ref) == hash(abbrev)


def test_process_references():
    ctx = Context()
    ctx.settings = {
        'references': DUMMY_REFS
    }
    ctx.markdown_text = """
    This is some dummy markdown text.
    
    This should be ref1 //ref1.
    
    This should be ref3 //ref3.
    
    This should be ref1 //ref1 again.
    """
    process_references(ctx)
    assert ctx.latex_refs == ['\\href{ref1_link}{ref1_name}', '\\href{ref3_link}{ref3_name}']
    assert ctx.markdown_text == """
    This is some dummy markdown text.
    
    This should be ref1 [ref1_name](ref1_link).
    
    This should be ref3 [ref3_name](ref3_link).
    
    This should be ref1 [ref1_name](ref1_link) again.
    """


def test_process_references_no_ref():
    ctx = Context()
    ctx.settings = {}
    ctx.markdown_text = """
    This is some dummy markdown text.
    
    This should be ref1 //ref1.
    
    This should be ref3 //ref3.
    
    This should be ref1 //ref1 again.
    """
    process_references(ctx)
    assert ctx.latex_refs == []
    assert ctx.markdown_text == """
    This is some dummy markdown text.
    
    This should be ref1 //ref1.
    
    This should be ref3 //ref3.
    
    This should be ref1 //ref1 again.
    """
