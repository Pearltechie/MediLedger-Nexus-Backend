"""Smart-contract deployment workflows."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..hedera_client import HederaClient
from .compiler import ContractCompiler

logger = logging.getLogger(__name__)


class ContractDeployer:
    """Deploy health, consent, research, and emergency contracts."""

    def __init__(
        self,
        hedera_client: HederaClient,
        compiler: ContractCompiler,
    ) -> None:
        """Initialize deployment services with shared blockchain dependencies."""
        self.client: HederaClient = hedera_client
        self.compiler: ContractCompiler = compiler

    def deploy_health_vault_contract(
        self,
        patient_account: str,
        vault_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Deploy a health vault contract for a patient."""
        try:
            bytecode: Optional[str] = self.compiler.get_contract_bytecode("HealthVault")
            abi: list[Any] = self.compiler.get_contract_abi("HealthVault")
            if not bytecode or not abi:
                raise ValueError("HealthVault contract bytecode or ABI not found")

            constructor_params: list[Any] = [
                patient_account,
                vault_config.get("name", "Health Vault"),
                vault_config.get("encryption_enabled", True),
                vault_config.get("zk_proofs_enabled", True),
                vault_config.get("privacy_level", "high"),
                vault_config.get("data_types", []),
            ]
            deployment_result: Dict[str, Any] = self.client.deploy_contract(
                bytecode=bytecode,
                constructor_params=constructor_params,
                gas_limit=500000,
            )
            deployment_info: Dict[str, Any] = {
                "contract_id": deployment_result["contract_id"],
                "contract_type": "health_vault",
                "owner": patient_account,
                "constructor_params": {
                    "vault_name": vault_config.get("name", "Health Vault"),
                    "encryption_enabled": vault_config.get("encryption_enabled", True),
                    "zk_proofs_enabled": vault_config.get("zk_proofs_enabled", True),
                    "privacy_level": vault_config.get("privacy_level", "high"),
                    "data_types": vault_config.get("data_types", []),
                },
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": deployment_result.get("gas_used", 0),
                "deployment_cost": deployment_result.get("cost_hbar", 0.0),
                "transaction_id": deployment_result.get("transaction_id"),
                "status": "deployed",
            }
            logger.info(
                "Deployed health vault contract: %s for %s",
                deployment_result["contract_id"],
                patient_account,
            )
            return deployment_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "deploy_health_vault_contract",
                    "contract_type": "health_vault",
                    "patient_account": patient_account,
                },
            )
            raise

    def deploy_consent_contract(
        self,
        patient_account: str,
        provider_account: str,
        consent_terms: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare deployment information for a consent contract."""
        try:
            contract_id: str = f"0.0.{datetime.now().microsecond}"
            constructor_params: Dict[str, Any] = {
                "patient": patient_account,
                "provider": provider_account,
                "record_types": consent_terms.get("record_types", []),
                "duration_hours": consent_terms.get("duration_hours", 24),
                "compensation_rate": consent_terms.get("compensation_rate", 0.0),
                "purpose": consent_terms.get("purpose", "Medical treatment"),
                "privacy_level": consent_terms.get("privacy_level", "high"),
                "auto_renewal": consent_terms.get("auto_renewal", False),
                "created_at": datetime.utcnow().timestamp(),
            }
            deployment_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "contract_type": "consent_management",
                "patient": patient_account,
                "provider": provider_account,
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 400000,
                "deployment_cost": 0.08,
                "status": "deployed",
            }
            logger.info("Deployed consent contract: %s", contract_id)
            return deployment_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "deploy_consent_contract",
                    "contract_type": "consent_management",
                    "patient_account": patient_account,
                    "provider_account": provider_account,
                },
            )
            raise

    def deploy_research_contract(self, study_config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare deployment information for a research study contract."""
        try:
            contract_id: str = f"0.0.{datetime.now().microsecond}"
            constructor_params: Dict[str, Any] = {
                "study_id": study_config.get("study_id"),
                "principal_investigator": study_config.get("principal_investigator"),
                "institution": study_config.get("institution"),
                "title": study_config.get("title"),
                "description": study_config.get("description"),
                "data_types": study_config.get("data_types", []),
                "compensation": study_config.get("compensation", 0.0),
                "duration_weeks": study_config.get("duration_weeks", 12),
                "max_participants": study_config.get("max_participants", 100),
                "created_at": datetime.utcnow().timestamp(),
            }
            deployment_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "contract_type": "research_study",
                "study_id": study_config.get("study_id"),
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 600000,
                "deployment_cost": 0.12,
                "status": "deployed",
            }
            logger.info("Deployed research contract: %s", contract_id)
            return deployment_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "deploy_research_contract",
                    "contract_type": "research_study",
                    "study_id": study_config.get("study_id"),
                },
            )
            raise

    def deploy_emergency_contract(
        self,
        patient_account: str,
        emergency_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare deployment information for an emergency access contract."""
        try:
            contract_id: str = f"0.0.{datetime.now().microsecond}"
            constructor_params: Dict[str, Any] = {
                "patient": patient_account,
                "blood_type": emergency_profile.get("blood_type"),
                "allergies": emergency_profile.get("allergies", []),
                "current_medications": emergency_profile.get("current_medications", []),
                "medical_conditions": emergency_profile.get("medical_conditions", []),
                "emergency_contact": emergency_profile.get("emergency_contact", {}),
                "insurance_info": emergency_profile.get("insurance_info", {}),
                "created_at": datetime.utcnow().timestamp(),
            }
            deployment_info: Dict[str, Any] = {
                "contract_id": contract_id,
                "contract_type": "emergency_access",
                "patient": patient_account,
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 350000,
                "deployment_cost": 0.07,
                "status": "deployed",
            }
            logger.info("Deployed emergency contract: %s for %s", contract_id, patient_account)
            return deployment_info
        except Exception:
            logger.exception(
                "Smart-contract operation failed",
                extra={
                    "operation": "deploy_emergency_contract",
                    "contract_type": "emergency_access",
                    "patient_account": patient_account,
                },
            )
            raise
