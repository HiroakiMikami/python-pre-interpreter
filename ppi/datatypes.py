from dataclasses import dataclass
from typing import List, Union, Any
from copy import deepcopy


@dataclass
class Range:
    start: int
    end: int

    def __hash__(self):
        return hash(tuple([self.start, self.end]))

    def __eq__(self, rhs: Any) -> bool:
        if isinstance(rhs, Range):
            return self.start == rhs.start and self.end == rhs.end
        else:
            return False


@dataclass
class Chunk:
    offset: Union[None, int]
    text: str

    def __hash__(self):
        return hash(tuple([self.offset, self.text]))

    def __eq__(self, rhs: Any) -> bool:
        if isinstance(rhs, Chunk):
            return self.offset == rhs.offset and self.text == rhs.text
        else:
            return False


@dataclass
class Line:
    chunks: List[Chunk]

    def __hash__(self):
        return hash(tuple(self.chunks))

    def __eq__(self, rhs: Any) -> bool:
        if isinstance(rhs, Line):
            return self.chunks == rhs.chunks
        else:
            return False

    def normalize(self):
        cs = []
        c = None
        for chunk in self.chunks:
            if chunk.text == "":
                continue
            if c is None:
                c = chunk
            elif c.offset is None:
                if chunk.offset is None:
                    c = Chunk(None, c.text + chunk.text)
                else:
                    cs.append(c)
                    c = chunk
            else:
                if c.offset + len(c.text) == chunk.offset:
                    c = Chunk(c.offset, c.text + chunk.text)
                else:
                    cs.append(c)
                    c = chunk
        if c is not None and c.text != "":
            cs.append(c)
        self.chunks = cs


@dataclass
class Patch:
    range: Range
    text: str

    def __hash__(self):
        return hash(tuple([self.range, self.text]))

    def __eq__(self, rhs: Any) -> bool:
        if isinstance(rhs, Patch):
            return self.range == rhs.range and self.text == rhs.text
        else:
            return False

    def apply(self, line: Line) -> Union[Line, None]:
        # Clone and normalize the line
        chunks = [deepcopy(c) for c in line.chunks]
        line = Line(chunks)
        line.normalize()

        if self.range.start < 0:
            line.chunks.append(Chunk(None, self.text))
        else:
            chunks = []
            for chunk in line.chunks:
                if chunk.offset is None:
                    chunks.append(chunk)
                else:
                    start = chunk.offset
                    end = chunk.offset + len(chunk.text)

                    if start <= self.range.start <= end and \
                            start <= self.range.end <= end:
                        # chunk1: [start:self.range.start]
                        length = self.range.start - start
                        chunks.append(Chunk(start, chunk.text[:length]))

                        chunks.append(Chunk(None, self.text))

                        # chunk2: [self.range.end:end]
                        offset = self.range.end - start
                        length = end - self.range.end
                        chunks.append(Chunk(self.range.end,
                                            chunk.text[offset:offset + length])
                                      )
                    else:
                        if end <= self.range.start or self.range.end <= start:
                            chunks.append(chunk)
                        else:
                            return None

            line = Line(chunks)

        # Normalize the line
        line.normalize()
        return line
