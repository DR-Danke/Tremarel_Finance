# Chore: Add LegalDesk service layer for deliverables, messages, and documents

## Metadata
issue_number: `189`
adw_id: `93e31eb3`
issue_json: ``

## Chore Description
`legaldesk_routes.py` directly imports and calls 3 repositories from the adapter/rest layer (lines 59-61): `ld_deliverable_repository`, `ld_document_repository`, and `ld_message_repository`. These repositories are used in 8 endpoints (deliverables: 4 endpoints, messages: 2 endpoints, documents: 2 endpoints) bypassing the Clean Architecture principle where the flow must be `adapter/rest → core/services → repository`. This violates the project's architecture standard and skips any business logic validation, authorization checks, or audit logging that should live in the service layer.

The fix is to create three new service classes that wrap the repository calls, matching the existing pattern used by `ld_case_service`, `ld_client_service`, `ld_specialist_service`, etc. Then update `legaldesk_routes.py` to import and use these services instead of the repositories directly.

## Relevant Files
Use these files to resolve the chore:

- `apps/Server/src/adapter/rest/legaldesk_routes.py` — The routes file that currently imports repositories directly. Lines 59-61 (imports) and lines 284-404 (8 endpoints) need to be updated.
- `apps/Server/src/repository/ld_deliverable_repository.py` — Deliverable repository with methods: `create`, `get_by_case`, `update`, `update_status`. The new service must wrap all 4 methods.
- `apps/Server/src/repository/ld_document_repository.py` — Document repository with methods: `create`, `get_by_case`. The new service must wrap both methods.
- `apps/Server/src/repository/ld_message_repository.py` — Message repository with methods: `create`, `get_by_case`. The new service must wrap both methods.
- `apps/Server/src/core/services/ld_client_service.py` — Reference implementation. Follow this exact pattern: import singleton repo, create service class with print logging, export singleton instance.
- `apps/Server/src/core/services/ld_case_service.py` — Another reference for the service pattern, demonstrates returning Optional for not-found cases.
- `apps/Server/tests/test_ld_client_service.py` — Reference test implementation. Follow this pattern: `@patch` the repository singleton, use `MagicMock` for db/models, assert delegation.
- `apps/Server/src/interface/legaldesk_dto.py` — Contains the DTOs used by the routes: `DeliverableCreateDTO`, `DeliverableUpdateDTO`, `DeliverableResponseDTO`, `MessageCreateDTO`, `MessageResponseDTO`, `DocumentCreateDTO`, `DocumentResponseDTO`.
- `apps/Server/src/models/ld_case_deliverable.py` — ORM model `LdCaseDeliverable` used for type hints in the deliverable service.
- `apps/Server/src/models/ld_case_document.py` — ORM model `LdCaseDocument` used for type hints in the document service.
- `apps/Server/src/models/ld_case_message.py` — ORM model `LdCaseMessage` used for type hints in the message service.

### New Files
- `apps/Server/src/core/services/ld_deliverable_service.py` — New service class wrapping `ld_deliverable_repository` with methods: `create_deliverable`, `get_case_deliverables`, `update_deliverable`, `update_deliverable_status`.
- `apps/Server/src/core/services/ld_message_service.py` — New service class wrapping `ld_message_repository` with methods: `create_message`, `get_case_messages`.
- `apps/Server/src/core/services/ld_document_service.py` — New service class wrapping `ld_document_repository` with methods: `create_document`, `get_case_documents`.
- `apps/Server/tests/test_ld_deliverable_service.py` — Unit tests for `LdDeliverableService`.
- `apps/Server/tests/test_ld_message_service.py` — Unit tests for `LdMessageService`.
- `apps/Server/tests/test_ld_document_service.py` — Unit tests for `LdDocumentService`.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create `ld_deliverable_service.py`
- Create `apps/Server/src/core/services/ld_deliverable_service.py`
- Follow the exact pattern from `ld_client_service.py`:
  - Import `ld_deliverable_repository` singleton from `src.repository.ld_deliverable_repository`
  - Import `LdCaseDeliverable` from `src.models.ld_case_deliverable` for type hints
  - Import `DeliverableCreateDTO`, `DeliverableUpdateDTO` from `src.interface.legaldesk_dto`
  - Create class `LdDeliverableService` with these methods:
    - `create_deliverable(self, db: Session, case_id: int, data: DeliverableCreateDTO) -> LdCaseDeliverable` — Sets `data.case_id = case_id`, calls `ld_deliverable_repository.create(db, data.model_dump())`
    - `get_case_deliverables(self, db: Session, case_id: int) -> list[LdCaseDeliverable]` — Delegates to `ld_deliverable_repository.get_by_case(db, case_id)`
    - `update_deliverable(self, db: Session, deliverable_id: int, data: DeliverableUpdateDTO) -> Optional[LdCaseDeliverable]` — Delegates to `ld_deliverable_repository.update(db, deliverable_id, data.model_dump(exclude_unset=True))`
    - `update_deliverable_status(self, db: Session, deliverable_id: int, status: str) -> Optional[LdCaseDeliverable]` — Delegates to `ld_deliverable_repository.update_status(db, deliverable_id, status)`
  - Add print logging for every method entry and exit (INFO level, tag `[LdDeliverableService]`)
  - Export singleton: `ld_deliverable_service = LdDeliverableService()`

### Step 2: Create `ld_message_service.py`
- Create `apps/Server/src/core/services/ld_message_service.py`
- Follow the same pattern:
  - Import `ld_message_repository` singleton
  - Import `LdCaseMessage` for type hints
  - Import `MessageCreateDTO` from `src.interface.legaldesk_dto`
  - Create class `LdMessageService` with these methods:
    - `create_message(self, db: Session, case_id: int, data: MessageCreateDTO) -> LdCaseMessage` — Builds `msg_data = data.model_dump()`, sets `msg_data["case_id"] = case_id`, calls `ld_message_repository.create(db, msg_data)`
    - `get_case_messages(self, db: Session, case_id: int, include_internal: bool = False) -> list[LdCaseMessage]` — Delegates to `ld_message_repository.get_by_case(db, case_id, include_internal=include_internal)`
  - Add print logging (tag `[LdMessageService]`)
  - Export singleton: `ld_message_service = LdMessageService()`

### Step 3: Create `ld_document_service.py`
- Create `apps/Server/src/core/services/ld_document_service.py`
- Follow the same pattern:
  - Import `ld_document_repository` singleton
  - Import `LdCaseDocument` for type hints
  - Import `DocumentCreateDTO` from `src.interface.legaldesk_dto`
  - Create class `LdDocumentService` with these methods:
    - `create_document(self, db: Session, case_id: int, data: DocumentCreateDTO) -> LdCaseDocument` — Builds `doc_data = data.model_dump()`, sets `doc_data["case_id"] = case_id`, calls `ld_document_repository.create(db, doc_data)`
    - `get_case_documents(self, db: Session, case_id: int) -> list[LdCaseDocument]` — Delegates to `ld_document_repository.get_by_case(db, case_id)`
  - Add print logging (tag `[LdDocumentService]`)
  - Export singleton: `ld_document_service = LdDocumentService()`

### Step 4: Update `legaldesk_routes.py` imports
- Remove lines 59-61 (the three direct repository imports):
  ```python
  from src.repository.ld_deliverable_repository import ld_deliverable_repository
  from src.repository.ld_document_repository import ld_document_repository
  from src.repository.ld_message_repository import ld_message_repository
  ```
- Add three new service imports (alongside the existing service imports on lines 16-22):
  ```python
  from src.core.services.ld_deliverable_service import ld_deliverable_service
  from src.core.services.ld_document_service import ld_document_service
  from src.core.services.ld_message_service import ld_message_service
  ```

### Step 5: Update deliverable endpoints in `legaldesk_routes.py`
- **`list_deliverables` (line 292)**: Change `ld_deliverable_repository.get_by_case(db, case_id)` to `ld_deliverable_service.get_case_deliverables(db, case_id)`
- **`create_deliverable` (lines 305-306)**: Remove `data.case_id = case_id` and `ld_deliverable_repository.create(db, data.model_dump())`. Replace with `ld_deliverable_service.create_deliverable(db, case_id, data)`
- **`update_deliverable` (line 320)**: Change `ld_deliverable_repository.update(db, deliverable_id, data.model_dump(exclude_unset=True))` to `ld_deliverable_service.update_deliverable(db, deliverable_id, data)`
- **`update_deliverable_status` (line 336)**: Change `ld_deliverable_repository.update_status(db, deliverable_id, body.status)` to `ld_deliverable_service.update_deliverable_status(db, deliverable_id, body.status)`

### Step 6: Update message endpoints in `legaldesk_routes.py`
- **`get_messages` (line 356)**: Change `ld_message_repository.get_by_case(db, case_id, include_internal=include_internal)` to `ld_message_service.get_case_messages(db, case_id, include_internal=include_internal)`
- **`create_message` (lines 369-371)**: Remove `msg_data = data.model_dump()`, `msg_data["case_id"] = case_id`, and `ld_message_repository.create(db, msg_data)`. Replace with `ld_message_service.create_message(db, case_id, data)`

### Step 7: Update document endpoints in `legaldesk_routes.py`
- **`list_documents` (line 388)**: Change `ld_document_repository.get_by_case(db, case_id)` to `ld_document_service.get_case_documents(db, case_id)`
- **`create_document` (lines 401-403)**: Remove `doc_data = data.model_dump()`, `doc_data["case_id"] = case_id`, and `ld_document_repository.create(db, doc_data)`. Replace with `ld_document_service.create_document(db, case_id, data)`

### Step 8: Create unit tests for `LdDeliverableService`
- Create `apps/Server/tests/test_ld_deliverable_service.py`
- Follow the pattern from `test_ld_client_service.py`:
  - Fixtures: `service()` returning `LdDeliverableService()`, `mock_db()` returning `MagicMock()`, `mock_deliverable()` returning a mock with id, case_id, title, status attributes
  - Test classes:
    - `TestCreateDeliverable`: Patch `ld_deliverable_repository`, verify `create` called with correct dict including case_id
    - `TestGetCaseDeliverables`: Verify delegation to `get_by_case`
    - `TestUpdateDeliverable`: Verify delegation to `update`, test not-found returns None
    - `TestUpdateDeliverableStatus`: Verify delegation to `update_status`, test not-found returns None

### Step 9: Create unit tests for `LdMessageService`
- Create `apps/Server/tests/test_ld_message_service.py`
- Test classes:
  - `TestCreateMessage`: Verify `create` called with correct dict including case_id
  - `TestGetCaseMessages`: Verify delegation to `get_by_case` with `include_internal` parameter

### Step 10: Create unit tests for `LdDocumentService`
- Create `apps/Server/tests/test_ld_document_service.py`
- Test classes:
  - `TestCreateDocument`: Verify `create` called with correct dict including case_id
  - `TestGetCaseDocuments`: Verify delegation to `get_by_case`

### Step 11: Run validation commands
- Run the full test suite to confirm zero regressions
- Verify no remaining direct repository imports in `legaldesk_routes.py`

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate the new services and ensure no regressions
- `cd apps/Server && python -m pytest tests/test_ld_deliverable_service.py tests/test_ld_message_service.py tests/test_ld_document_service.py -v` — Run just the new service tests to confirm they pass
- `cd apps/Server && python -c "from src.core.services.ld_deliverable_service import ld_deliverable_service; from src.core.services.ld_message_service import ld_message_service; from src.core.services.ld_document_service import ld_document_service; print('All services import OK')"` — Verify all three new service modules import cleanly
- `cd apps/Server && python -c "from src.adapter.rest.legaldesk_routes import router; print('Routes import OK')"` — Verify the updated routes file imports cleanly with no direct repository references
- `cd apps/Server && grep -n 'from src.repository.ld_deliverable_repository\|from src.repository.ld_document_repository\|from src.repository.ld_message_repository' src/adapter/rest/legaldesk_routes.py; echo "Exit code: $?"` — Verify no direct repository imports remain in routes (should find 0 matches)

## Notes
- The three new services are thin wrappers following the established delegation pattern. They exist to enforce Clean Architecture and provide a proper hook point for future business logic (e.g., validation, authorization, audit logging).
- The `create_deliverable`, `create_message`, and `create_document` service methods accept `case_id` as a separate parameter and handle setting it on the data dict internally. This moves that responsibility out of the routes layer where it doesn't belong.
- The `update_deliverable` service method accepts the DTO directly and calls `model_dump(exclude_unset=True)` internally, matching how `ld_client_service.update` handles partial updates.
- No frontend changes are required — this is purely a backend architectural refactor.
