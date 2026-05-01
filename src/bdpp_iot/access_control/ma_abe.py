from __future__ import annotations

from dataclasses import dataclass
import hashlib
import secrets

from bdpp_iot.blockchain.ledger import Ledger
from bdpp_iot.access_control.policy import parse_policy


@dataclass(frozen=True)
class Authority:
    name: str
    attributes: frozenset[str]


@dataclass
class UserKey:
    user_id: str
    attributes: set[str]
    version: int
    authority_fragments: dict[str, set[str]]


@dataclass(frozen=True)
class AccessCiphertext:
    policy: str
    encrypted_key_ref: str
    required_authorities: frozenset[str]
    version_bound: int


class MultiAuthorityAccessControl:
    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger
        self.authorities = [
            Authority("AA_ORG", frozenset({"hospital_a", "hospital_b", "research_lab"})),
            Authority("AA_ROLE", frozenset({"doctor", "cardiology_researcher", "admin"})),
            Authority("AA_DATA", frozenset({"heart_rate", "temperature", "blood_pressure", "glucose"})),
            Authority("AA_LOCATION", frozenset({"ward_a", "ward_b", "remote"})),
        ]
        self.attribute_owner = {
            attribute: authority.name
            for authority in self.authorities
            for attribute in authority.attributes
        }

    def issue_key(self, user_id: str, attributes: set[str]) -> UserKey:
        self.ledger.register_user(user_id)
        fragments: dict[str, set[str]] = {}
        for attribute in attributes:
            authority_name = self.attribute_owner.get(attribute, "AA_UNKNOWN")
            fragments.setdefault(authority_name, set()).add(attribute)
        return UserKey(
            user_id=user_id,
            attributes=set(attributes),
            version=self.ledger.get_version(user_id),
            authority_fragments=fragments,
        )

    def can_decrypt(self, key: UserKey, policy: set[str] | str, check_revocation: bool = True) -> bool:
        if isinstance(policy, str):
            policy_ok = parse_policy(policy).evaluate(key.attributes)
        else:
            policy_ok = policy.issubset(key.attributes)
        if not check_revocation:
            return policy_ok
        version_ok = key.version == self.ledger.get_version(key.user_id)
        return policy_ok and version_ok

    def encrypt_key(self, symmetric_key: str, policy: str, owner_user_id: str = "data_owner") -> AccessCiphertext:
        parsed = parse_policy(policy)
        required_authorities = frozenset(
            self.attribute_owner.get(attribute, "AA_UNKNOWN")
            for attribute in parsed.required_attributes()
        )
        digest = hashlib.sha256(f"{symmetric_key}:{policy}:{secrets.token_hex(8)}".encode("utf-8")).hexdigest()
        return AccessCiphertext(
            policy=policy,
            encrypted_key_ref=f"abe_ct_{digest[:24]}",
            required_authorities=required_authorities,
            version_bound=self.ledger.get_version(owner_user_id),
        )

    def decrypt_key(self, ciphertext: AccessCiphertext, key: UserKey, check_revocation: bool = True) -> bool:
        return self.can_decrypt(key, ciphertext.policy, check_revocation=check_revocation)

    def collusion_can_decrypt(
        self,
        keys: list[UserKey],
        policy: str,
        check_revocation: bool = True,
    ) -> bool:
        """Simulate anti-collusion by rejecting attribute pooling across identities.

        In real CP-ABE, keys are randomized per identity and users cannot simply merge
        attributes. For this coursework model, colluding users are tested individually:
        the group succeeds only if one complete, non-revoked key satisfies the policy.
        """

        return any(self.can_decrypt(key, policy, check_revocation=check_revocation) for key in keys)
