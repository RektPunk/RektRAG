from pydantic import BaseModel, Field


class DocNode(BaseModel):
    ref_id: str
    parent_id: str = ""
    level: int = Field(exclude=True)
    title: str = ""
    content: str = ""
    summary: str = ""
    page_index: int | None = None
    children: list["DocNode"] = Field(default_factory=list)

    def __index_map(self) -> dict:
        return self.model_dump(exclude={"children"})

    def get_index_map(self) -> dict[str, dict[str, str | int]]:
        index_map = {self.ref_id: self.__index_map()}
        for child in self.children:
            index_map.update(child.get_index_map())
        return index_map

    def get_slim_tree(self) -> dict:
        node_dict = self.model_dump(exclude={"parent_id", "content", "children"})
        if self.children:
            node_dict["children"] = [child.get_slim_tree() for child in self.children]
        return node_dict


DocNode.model_rebuild()
