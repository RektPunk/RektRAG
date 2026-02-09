from docling.document_converter import DocumentConverter
from docling_core.types.doc import (
    CodeItem,
    FormulaItem,
    ListItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
)

from rektrag.schema import DocNode

ALLOWED_TYPES = (
    TextItem,
    TableItem,
    SectionHeaderItem,
    TitleItem,
    ListItem,
    CodeItem,
    FormulaItem,
)


def build_map(path: str, doc_hash: str) -> DocNode:
    converter = DocumentConverter()
    result = converter.convert(path)
    doc = result.document
    root = DocNode(ref_id=f"{doc_hash}", level=0)
    stack = [root]
    for item, _ in doc.iterate_items():
        if not isinstance(item, ALLOWED_TYPES):
            continue
        text = item.text.strip() if hasattr(item, "text") else ""
        page_no = item.prov[0].page_no if item.prov else None
        if isinstance(item, (TitleItem, SectionHeaderItem)):
            current_level = getattr(item, "level", 1)
            while len(stack) > 1 and stack[-1].level >= current_level:
                stack.pop()
            parent_node = stack[-1]
            new_node = DocNode(
                ref_id=f"{doc_hash}/{item.self_ref.split('/')[-1]}",
                title=text,
                level=current_level,
                page_index=page_no,
                parent_id=parent_node.ref_id,
            )
            parent_node.children.append(new_node)
            stack.append(new_node)
        else:
            current_node = stack[-1]
            if isinstance(item, TableItem):
                current_node.content += f"\n{item.export_to_markdown(doc)}\n"
            elif isinstance(item, CodeItem):
                current_node.content += f"\n```\n{text}\n```\n"
            else:
                current_node.content += f"{text}\n"

            if current_node.page_index is None and item.prov:
                current_node.page_index = page_no

    return root
