"""Smart-contract artifact loading and compilation boundaries."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ContractCompiler:
    """Load compiled Solidity artifacts used by contract services.

    Compilation itself is performed by the repository's Solidity toolchain.
    This class owns the artifact boundary so deployment and execution code do
    not need to know where ABI and bytecode files are stored.
    """

    CONTRACT_NAMES: List[str] = [
        "HealthVault",
        "ConsentManager",
        "ResearchStudy",
        "EmergencyAccess",
    ]

    def __init__(self, artifacts_root: Optional[Path] = None) -> None:
        """Initialize the compiler with an optional artifact directory."""
        self.artifacts_root: Path = artifacts_root or self._default_artifacts_root()

    def _default_artifacts_root(self) -> Path:
        """Return the repository's Foundry artifact directory."""
        return Path(__file__).resolve().parents[5] / "contracts" / "out"

    def _artifact_path(self, contract_name: str) -> Path:
        """Return the artifact path for a Solidity contract."""
        return (
            self.artifacts_root
            / contract_name
            / f"{contract_name}.sol"
            / f"{contract_name}.json"
        )

    def _load_artifact(self, contract_name: str) -> Dict[str, Any]:
        """Load one compiled contract artifact as a JSON mapping."""
        artifact_path: Path = self._artifact_path(contract_name)
        if not artifact_path.exists():
            logger.warning("Contract artifact not found: %s", artifact_path)
            return {}

        try:
            with artifact_path.open("r", encoding="utf-8") as artifact_file:
                artifact: Dict[str, Any] = json.load(artifact_file)
            return artifact
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Failed to load artifact for %s: %s", contract_name, error)
            return {}

    def load_contract_abis(self) -> Dict[str, List[Any]]:
        """Load all available contract ABIs keyed by normalized contract name."""
        abis: Dict[str, List[Any]] = {}
        for contract_name in self.CONTRACT_NAMES:
            artifact: Dict[str, Any] = self._load_artifact(contract_name)
            abi: Any = artifact.get("abi", [])
            abis[contract_name.lower()] = abi if isinstance(abi, list) else []
        return abis

    def get_contract_abi(self, contract_name: str) -> List[Any]:
        """Load one contract ABI."""
        artifact: Dict[str, Any] = self._load_artifact(contract_name)
        abi: Any = artifact.get("abi", [])
        return abi if isinstance(abi, list) else []

    def get_contract_bytecode(self, contract_name: str) -> Optional[str]:
        """Return compiled contract bytecode, if the artifact contains it."""
        artifact: Dict[str, Any] = self._load_artifact(contract_name)
        bytecode: Any = artifact.get("bytecode", {})
        if not isinstance(bytecode, dict):
            return None
        bytecode_object: Any = bytecode.get("object")
        return bytecode_object if isinstance(bytecode_object, str) and bytecode_object else None

    def compile_contract(self, contract_name: str) -> Dict[str, Any]:
        """Return the compiled artifact for a contract.

        The actual Solidity compilation is intentionally delegated to Foundry;
        this method provides a typed application boundary around its output.
        """
        artifact: Dict[str, Any] = self._load_artifact(contract_name)
        if not artifact:
            raise FileNotFoundError(f"Compiled artifact not found for {contract_name}")
        return artifact
