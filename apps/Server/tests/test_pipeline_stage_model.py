"""Tests for PipelineStage and StageTransition models and DTOs."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.pipeline_stage_dto import (
    PipelineStageCreateDTO,
    PipelineStageListResponseDTO,
    PipelineStageResponseDTO,
    PipelineStageUpdateDTO,
)
from src.interface.stage_transition_dto import (
    StageTransitionCreateDTO,
    StageTransitionListResponseDTO,
    StageTransitionResponseDTO,
)
from src.models.pipeline_stage import PipelineStage
from src.models.stage_transition import StageTransition


# ============================================================================
# PipelineStageCreateDTO Tests
# ============================================================================


def test_pipeline_stage_create_dto_valid() -> None:
    """Test valid creation DTO with all fields."""
    entity_id = uuid4()
    dto = PipelineStageCreateDTO(
        entity_id=entity_id,
        name="qualified",
        display_name="Qualified",
        order_index=2,
        color="#A5D6A7",
        is_default=False,
    )
    assert dto.entity_id == entity_id
    assert dto.name == "qualified"
    assert dto.display_name == "Qualified"
    assert dto.order_index == 2
    assert dto.color == "#A5D6A7"
    assert dto.is_default is False
    print("INFO [TestPipelineStage]: test_pipeline_stage_create_dto_valid - PASSED")


def test_pipeline_stage_create_dto_minimal() -> None:
    """Test valid creation DTO with only required fields."""
    entity_id = uuid4()
    dto = PipelineStageCreateDTO(
        entity_id=entity_id,
        name="lead",
        display_name="Lead",
        order_index=0,
    )
    assert dto.entity_id == entity_id
    assert dto.name == "lead"
    assert dto.display_name == "Lead"
    assert dto.order_index == 0
    assert dto.color is None
    assert dto.is_default is False
    print("INFO [TestPipelineStage]: test_pipeline_stage_create_dto_minimal - PASSED")


def test_pipeline_stage_create_dto_empty_name() -> None:
    """Test that empty name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        PipelineStageCreateDTO(
            entity_id=uuid4(),
            name="",
            display_name="Empty",
            order_index=0,
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestPipelineStage]: test_pipeline_stage_create_dto_empty_name - PASSED")


def test_pipeline_stage_create_dto_negative_order() -> None:
    """Test that negative order_index is rejected (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        PipelineStageCreateDTO(
            entity_id=uuid4(),
            name="lead",
            display_name="Lead",
            order_index=-1,
        )
    assert "order_index" in str(exc_info.value)
    print("INFO [TestPipelineStage]: test_pipeline_stage_create_dto_negative_order - PASSED")


# ============================================================================
# PipelineStageUpdateDTO Tests
# ============================================================================


def test_pipeline_stage_update_dto_partial() -> None:
    """Test partial update with only some fields."""
    dto = PipelineStageUpdateDTO(
        display_name="Updated Name",
        color="#FF0000",
    )
    assert dto.display_name == "Updated Name"
    assert dto.color == "#FF0000"
    assert dto.name is None
    assert dto.order_index is None
    assert dto.is_default is None
    assert dto.is_active is None
    print("INFO [TestPipelineStage]: test_pipeline_stage_update_dto_partial - PASSED")


def test_pipeline_stage_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = PipelineStageUpdateDTO()
    assert dto.name is None
    assert dto.display_name is None
    assert dto.order_index is None
    assert dto.color is None
    assert dto.is_default is None
    assert dto.is_active is None
    print("INFO [TestPipelineStage]: test_pipeline_stage_update_dto_empty - PASSED")


# ============================================================================
# PipelineStageResponseDTO Tests
# ============================================================================


def test_pipeline_stage_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_stage = MagicMock(spec=PipelineStage)
    mock_stage.id = uuid4()
    mock_stage.entity_id = uuid4()
    mock_stage.name = "proposal"
    mock_stage.display_name = "Proposal"
    mock_stage.order_index = 3
    mock_stage.color = "#FFE082"
    mock_stage.is_default = False
    mock_stage.is_active = True
    mock_stage.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_stage.updated_at = None

    dto = PipelineStageResponseDTO.model_validate(mock_stage, from_attributes=True)
    assert dto.id == mock_stage.id
    assert dto.entity_id == mock_stage.entity_id
    assert dto.name == "proposal"
    assert dto.display_name == "Proposal"
    assert dto.order_index == 3
    assert dto.color == "#FFE082"
    assert dto.is_default is False
    assert dto.is_active is True
    assert dto.updated_at is None
    print("INFO [TestPipelineStage]: test_pipeline_stage_response_dto_from_attributes - PASSED")


# ============================================================================
# PipelineStageListResponseDTO Tests
# ============================================================================


def test_pipeline_stage_list_response_dto() -> None:
    """Test list response with total count."""
    stage_id = uuid4()
    entity_id = uuid4()
    now = datetime(2026, 2, 1, 12, 0, 0)

    response_dto = PipelineStageResponseDTO(
        id=stage_id,
        entity_id=entity_id,
        name="lead",
        display_name="Lead",
        order_index=0,
        color="#90CAF9",
        is_default=True,
        is_active=True,
        created_at=now,
        updated_at=None,
    )

    list_dto = PipelineStageListResponseDTO(
        stages=[response_dto],
        total=1,
    )
    assert len(list_dto.stages) == 1
    assert list_dto.total == 1
    assert list_dto.stages[0].name == "lead"
    print("INFO [TestPipelineStage]: test_pipeline_stage_list_response_dto - PASSED")


# ============================================================================
# PipelineStage Model Tests
# ============================================================================


def test_pipeline_stage_model_repr() -> None:
    """Test PipelineStage model __repr__ method."""
    stage = PipelineStage()
    stage.id = uuid4()
    stage.name = "qualified"
    stage.order_index = 2

    repr_str = repr(stage)
    assert "qualified" in repr_str
    assert "PipelineStage" in repr_str
    print("INFO [TestPipelineStage]: test_pipeline_stage_model_repr - PASSED")


def test_pipeline_stage_model_tablename() -> None:
    """Test PipelineStage model has correct table name."""
    assert PipelineStage.__tablename__ == "pipeline_stages"
    print("INFO [TestPipelineStage]: test_pipeline_stage_model_tablename - PASSED")


# ============================================================================
# StageTransitionCreateDTO Tests
# ============================================================================


def test_stage_transition_create_dto_valid() -> None:
    """Test valid stage transition creation DTO with all fields."""
    prospect_id = uuid4()
    entity_id = uuid4()
    from_stage_id = uuid4()
    to_stage_id = uuid4()
    user_id = uuid4()

    dto = StageTransitionCreateDTO(
        prospect_id=prospect_id,
        entity_id=entity_id,
        from_stage_id=from_stage_id,
        to_stage_id=to_stage_id,
        transitioned_by=user_id,
        notes="Moved to next stage after meeting",
    )
    assert dto.prospect_id == prospect_id
    assert dto.entity_id == entity_id
    assert dto.from_stage_id == from_stage_id
    assert dto.to_stage_id == to_stage_id
    assert dto.transitioned_by == user_id
    assert dto.notes == "Moved to next stage after meeting"
    print("INFO [TestPipelineStage]: test_stage_transition_create_dto_valid - PASSED")


def test_stage_transition_create_dto_no_from_stage() -> None:
    """Test transition DTO with null from_stage_id (initial assignment)."""
    dto = StageTransitionCreateDTO(
        prospect_id=uuid4(),
        entity_id=uuid4(),
        from_stage_id=None,
        to_stage_id=uuid4(),
        transitioned_by=None,
        notes=None,
    )
    assert dto.from_stage_id is None
    assert dto.transitioned_by is None
    assert dto.notes is None
    print("INFO [TestPipelineStage]: test_stage_transition_create_dto_no_from_stage - PASSED")


# ============================================================================
# StageTransitionResponseDTO Tests
# ============================================================================


def test_stage_transition_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_transition = MagicMock(spec=StageTransition)
    mock_transition.id = uuid4()
    mock_transition.prospect_id = uuid4()
    mock_transition.entity_id = uuid4()
    mock_transition.from_stage_id = uuid4()
    mock_transition.to_stage_id = uuid4()
    mock_transition.transitioned_by = uuid4()
    mock_transition.notes = "Qualified after demo"
    mock_transition.created_at = datetime(2026, 2, 15, 14, 0, 0)

    dto = StageTransitionResponseDTO.model_validate(mock_transition, from_attributes=True)
    assert dto.id == mock_transition.id
    assert dto.prospect_id == mock_transition.prospect_id
    assert dto.from_stage_id == mock_transition.from_stage_id
    assert dto.to_stage_id == mock_transition.to_stage_id
    assert dto.notes == "Qualified after demo"
    print("INFO [TestPipelineStage]: test_stage_transition_response_dto_from_attributes - PASSED")


# ============================================================================
# StageTransitionListResponseDTO Tests
# ============================================================================


def test_stage_transition_list_response_dto() -> None:
    """Test list response with total count."""
    transition_id = uuid4()
    now = datetime(2026, 2, 1, 12, 0, 0)

    response_dto = StageTransitionResponseDTO(
        id=transition_id,
        prospect_id=uuid4(),
        entity_id=uuid4(),
        from_stage_id=uuid4(),
        to_stage_id=uuid4(),
        transitioned_by=uuid4(),
        notes="Initial assignment",
        created_at=now,
    )

    list_dto = StageTransitionListResponseDTO(
        transitions=[response_dto],
        total=1,
    )
    assert len(list_dto.transitions) == 1
    assert list_dto.total == 1
    print("INFO [TestPipelineStage]: test_stage_transition_list_response_dto - PASSED")


# ============================================================================
# StageTransition Model Tests
# ============================================================================


def test_stage_transition_model_repr() -> None:
    """Test StageTransition model __repr__ method."""
    transition = StageTransition()
    transition.id = uuid4()
    transition.prospect_id = uuid4()
    transition.from_stage_id = uuid4()
    transition.to_stage_id = uuid4()

    repr_str = repr(transition)
    assert "StageTransition" in repr_str
    print("INFO [TestPipelineStage]: test_stage_transition_model_repr - PASSED")


def test_stage_transition_model_tablename() -> None:
    """Test StageTransition model has correct table name."""
    assert StageTransition.__tablename__ == "stage_transitions"
    print("INFO [TestPipelineStage]: test_stage_transition_model_tablename - PASSED")
