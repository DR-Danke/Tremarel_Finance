"""Models layer - database models and entities."""

from src.models.document import Document
from src.models.entity import Entity
from src.models.inventory_movement import InventoryMovement
from src.models.meeting_record import MeetingRecord
from src.models.person import Person
from src.models.pipeline_stage import PipelineStage
from src.models.resource import Resource
from src.models.prospect import Prospect
from src.models.restaurant import Restaurant
from src.models.stage_transition import StageTransition
from src.models.user import User
from src.models.user_entity import UserEntity
from src.models.user_restaurant import UserRestaurant

# Legal Desk models
from src.models.ld_client import LdClient
from src.models.ld_specialist import LdSpecialist
from src.models.ld_specialist_expertise import LdSpecialistExpertise
from src.models.ld_specialist_jurisdiction import LdSpecialistJurisdiction
from src.models.ld_case import LdCase
from src.models.ld_case_specialist import LdCaseSpecialist
from src.models.ld_case_deliverable import LdCaseDeliverable
from src.models.ld_case_message import LdCaseMessage
from src.models.ld_case_document import LdCaseDocument
from src.models.ld_pricing_history import LdPricingHistory
from src.models.ld_specialist_score import LdSpecialistScore

__all__ = [
    "User",
    "Entity",
    "Prospect",
    "PipelineStage",
    "StageTransition",
    "UserEntity",
    "MeetingRecord",
    "Restaurant",
    "UserRestaurant",
    "Person",
    "Resource",
    "Document",
    "InventoryMovement",
    # Legal Desk models
    "LdClient",
    "LdSpecialist",
    "LdSpecialistExpertise",
    "LdSpecialistJurisdiction",
    "LdCase",
    "LdCaseSpecialist",
    "LdCaseDeliverable",
    "LdCaseMessage",
    "LdCaseDocument",
    "LdPricingHistory",
    "LdSpecialistScore",
]
