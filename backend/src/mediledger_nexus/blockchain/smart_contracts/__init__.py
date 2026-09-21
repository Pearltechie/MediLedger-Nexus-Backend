"""Modular smart-contract services for MediLedger Nexus."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...utils.formatters import DataFormatter
from ..hedera_client import HederaClient
from .compiler import ContractCompiler
from .deployer import ContractDeployer
from .executor import ContractExecutor


class SmartContractService:
    """Compatibility façade over compiler, deployer, and executor services."""

    def __init__(self, hedera_client: Optional[HederaClient] = None) -> None:
        """Initialize the modular smart-contract services."""
        self.client: HederaClient = hedera_client or HederaClient()
        self.formatter: DataFormatter = DataFormatter()
        self.compiler: ContractCompiler = ContractCompiler()
        self.deployer: ContractDeployer = ContractDeployer(self.client, self.compiler)
        self.executor: ContractExecutor = ContractExecutor(self.client)

        self.health_vault_contract: str = os.getenv("HEALTH_VAULT_CONTRACT", "0.0.1001")
        self.consent_contract: str = os.getenv("CONSENT_CONTRACT", "0.0.1002")
        self.research_contract: str = os.getenv("RESEARCH_CONTRACT", "0.0.1003")
        self.emergency_contract: str = os.getenv("EMERGENCY_CONTRACT", "0.0.1004")
        self.contract_abis: Dict[str, List[Any]] = self.compiler.load_contract_abis()

    def _load_contract_abis(self) -> Dict[str, List[Any]]:
        """Load contract ABIs through the compiler component."""
        return self.compiler.load_contract_abis()

    def _get_contract_bytecode(self, contract_name: str) -> Optional[str]:
        """Load contract bytecode through the compiler component."""
        return self.compiler.get_contract_bytecode(contract_name)

    def deploy_health_vault_contract(
        self,
        patient_account: str,
        vault_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate health-vault deployment."""
        return self.deployer.deploy_health_vault_contract(patient_account, vault_config)

    def create_health_record(
        self,
        contract_id: str,
        record_data: Dict[str, Any],
        access_permissions: List[str],
    ) -> Dict[str, Any]:
        """Delegate health-record creation."""
        return self.executor.create_health_record(contract_id, record_data, access_permissions)

    def grant_record_access(
        self,
        contract_id: str,
        record_id: str,
        grantee_account: str,
        access_level: str,
        duration_hours: int,
    ) -> Dict[str, Any]:
        """Delegate record-access grants."""
        return self.executor.grant_record_access(
            contract_id, record_id, grantee_account, access_level, duration_hours
        )

    def revoke_record_access(
        self,
        contract_id: str,
        record_id: str,
        grantee_account: str,
    ) -> Dict[str, Any]:
        """Delegate record-access revocation."""
        return self.executor.revoke_record_access(contract_id, record_id, grantee_account)

    def deploy_consent_contract(
        self,
        patient_account: str,
        provider_account: str,
        consent_terms: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate consent-contract deployment."""
        return self.deployer.deploy_consent_contract(
            patient_account, provider_account, consent_terms
        )

    def activate_consent(self, contract_id: str) -> Dict[str, Any]:
        """Delegate consent activation."""
        return self.executor.activate_consent(contract_id)

    def revoke_consent(
        self,
        contract_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delegate consent revocation."""
        return self.executor.revoke_consent(contract_id, reason)

    def deploy_research_contract(self, study_config: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate research-contract deployment."""
        return self.deployer.deploy_research_contract(study_config)

    def join_research_study(
        self,
        contract_id: str,
        participant_account: str,
        consent_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate research-study participation."""
        return self.executor.join_research_study(
            contract_id, participant_account, consent_data
        )

    def deploy_emergency_contract(
        self,
        patient_account: str,
        emergency_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate emergency-contract deployment."""
        return self.deployer.deploy_emergency_contract(patient_account, emergency_profile)

    def request_emergency_access(
        self,
        contract_id: str,
        requester_account: str,
        emergency_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Delegate emergency-access requests."""
        return self.executor.request_emergency_access(
            contract_id, requester_account, emergency_details
        )

    def get_contract_state(self, contract_id: str) -> Dict[str, Any]:
        """Delegate contract-state reads."""
        return self.executor.get_contract_state(contract_id)

    def call_contract_function(
        self,
        contract_id: str,
        function_name: str,
        parameters: Dict[str, Any],
        gas_limit: int = 300000,
    ) -> Dict[str, Any]:
        """Delegate ABI function execution."""
        return self.executor.call_contract_function(
            contract_id, function_name, parameters, gas_limit
        )


__all__: List[str] = [
    "ContractCompiler",
    "ContractDeployer",
    "ContractExecutor",
    "SmartContractService",
]
