from __future__ import annotations

from dataclasses import dataclass


class PolicySyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class PolicyNode:
    op: str
    value: str | None = None
    left: "PolicyNode | None" = None
    right: "PolicyNode | None" = None

    def evaluate(self, attributes: set[str]) -> bool:
        if self.op == "ATTR":
            return self.value in attributes
        if self.op == "AND":
            return bool(self.left and self.right and self.left.evaluate(attributes) and self.right.evaluate(attributes))
        if self.op == "OR":
            return bool(self.left and self.right and (self.left.evaluate(attributes) or self.right.evaluate(attributes)))
        raise PolicySyntaxError(f"Unsupported policy operation: {self.op}")

    def required_attributes(self) -> set[str]:
        if self.op == "ATTR":
            return {self.value or ""}
        attrs: set[str] = set()
        if self.left:
            attrs.update(self.left.required_attributes())
        if self.right:
            attrs.update(self.right.required_attributes())
        return attrs


class PolicyParser:
    def __init__(self, text: str) -> None:
        self.tokens = self._tokenize(text)
        self.index = 0

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        spaced = text.replace("(", " ( ").replace(")", " ) ")
        return [token.strip() for token in spaced.split() if token.strip()]

    def parse(self) -> PolicyNode:
        if not self.tokens:
            raise PolicySyntaxError("Policy cannot be empty.")
        node = self._parse_or()
        if self.index != len(self.tokens):
            raise PolicySyntaxError(f"Unexpected token: {self.tokens[self.index]}")
        return node

    def _peek(self) -> str | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def _consume(self) -> str:
        token = self._peek()
        if token is None:
            raise PolicySyntaxError("Unexpected end of policy.")
        self.index += 1
        return token

    def _parse_or(self) -> PolicyNode:
        node = self._parse_and()
        while (self._peek() or "").upper() == "OR":
            self._consume()
            node = PolicyNode("OR", left=node, right=self._parse_and())
        return node

    def _parse_and(self) -> PolicyNode:
        node = self._parse_term()
        while (self._peek() or "").upper() == "AND":
            self._consume()
            node = PolicyNode("AND", left=node, right=self._parse_term())
        return node

    def _parse_term(self) -> PolicyNode:
        token = self._consume()
        if token == "(":
            node = self._parse_or()
            if self._consume() != ")":
                raise PolicySyntaxError("Missing closing parenthesis.")
            return node
        if token == ")":
            raise PolicySyntaxError("Unexpected closing parenthesis.")
        if token.upper() in {"AND", "OR"}:
            raise PolicySyntaxError(f"Unexpected operator: {token}")
        return PolicyNode("ATTR", value=token)


def parse_policy(policy: str) -> PolicyNode:
    return PolicyParser(policy).parse()

