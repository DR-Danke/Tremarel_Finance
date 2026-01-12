# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Cashback & Loyalty Program - Finkargo

## Project Status: Planning & Specification Phase

**⚠️ IMPORTANT**: This repository currently contains **documentation and architecture specifications only**. No code implementation exists yet.

### What's Here
- ✅ Comprehensive requirements documentation (`Extracted_Requirements/`)
- ✅ Architecture diagrams and flowcharts
- ✅ Business rules and use cases (WRSPM model)
- ✅ Database schema design (PostgreSQL)
- ✅ Technical specifications for MVP development
- ✅ TAC (Tactical Agentic Coding) methodology integration

### What's Not Here (Yet)
- ❌ No frontend code (React + TypeScript + Vite)
- ❌ No backend code (FastAPI + Python)
- ❌ No package.json or requirements.txt
- ❌ No build/test/run commands

### Next Steps for Implementation
When development begins, follow these steps:

1. **Review Requirements**:
   ```bash
   # Read comprehensive requirements
   cat Extracted_Requirements/20251015_cashback_loyalty_requirements.md

   # Review architecture diagrams
   cat Extracted_Requirements/20251015_cashback_flowcharts.md
   ```

2. **Create Project Structure**:
   - Initialize frontend: `npm create vite@latest client -- --template react-ts`
   - Initialize backend: `poetry init` or `uv init` for Python project
   - Set up monorepo structure if needed

3. **Follow Architecture Guidelines Below**

### Key Business Context
- **Domain**: Fintech loyalty/cashback program for financing customers
- **Markets**: Colombia and Mexico
- **Core Flow**: Early payment (30+ days) → 6% cashback on interest → Wallet credits → Redeem for future payments
- **MVP Approach**: Manual redemption first, then automate (see Phase 1 in requirements)

---

## Core Principles
**CRITICAL**: All code MUST follow Clean Architecture and SOLID design principles. Never violate these principles - refactoring will be required if they are not followed.

## Requirements Definition and Specifications
1. For each new requirement, analyze the underlying goal
2. Spend time strategically upfront, to reduce cost and time later on
3. Document the requirement understanding and tag them as functional or non functional requirements 
4. Use the WRSPM model

## Architecture
1. Divide the solution into subsystems
2. Divide the subsystems into modules
3. A subsystem is a portion of the whole system that is independent and holds independent value
4. Modules are components  of a subsystem which cannot function as a standalone
5. Modules should be loosely coupled but have strong cohesion
6. Each module should have a set and well defined purpose

## Agentic Code Architecture Principles
**CRITICAL**: Design your codebase for AI agent navigation and autonomous operation. Agents are brilliant but ephemeral - they start each session with zero context. Make your architecture agent-friendly to maximize autonomous engineering capability.

### Agent Navigation Optimization
**The Agent Navigation Problem**: Every time you boot up a new agent, it must explore and understand your codebase structure. Poor architecture compounds this problem exponentially across hundreds of agent sessions.

**Solutions**:
1. **Clear Entry Points**: Use obvious main files (e.g., `main.py`, `server.py`, `app.tsx`, `index.tsx`)
2. **Architectural Shortcuts**: Simple decisions like client/server separation cut search space in half
3. **Consistency Over Cleverness**: Reuse the same patterns, folder structures, function names, and file names throughout
4. **Consistency as Defense**: Against complexity - consistent patterns work for both humans and agents at scale

### File Organization Standards
1. **File Size Limits**: Soft limit of 1000 lines per file for optimal agent processing
2. **Single Responsibility**: One clear purpose per file makes navigation predictable
3. **Constant Files**: Centralize unchanging configuration and constants
4. **Documentation Distribution**: Place README.md and CLAUDE.md files throughout major subsystems
5. **Test Structure Synchronization**: Mirror your application structure in tests (e.g., `src/core/` → `tests/core/`)
6. **Clear Separation**: Organize by concern (client/server, controllers/services/repositories)

### Naming Conventions for Agent Discoverability
**Information-Dense Keywords (IDKs)**: Every name is an opportunity to guide your agent.

**Good IDK Examples**:
- `UserAuthenticationService` (clear, specific, searchable)
- `PaymentTransactionRepository` (describes exact responsibility)
- `CustomerInvoiceValidator` (unambiguous purpose)

**Bad IDK Examples**:
- `DataRequest` (too generic, "data" appears everywhere)
- `Handler` (what does it handle?)
- `Utils` (catch-all with no semantic meaning)

**IDK Naming Rules**:
1. Use meaningful, verbose names for types, classes, functions, variables, and directories
2. Avoid generic terms like "data", "handler", "manager", "util" without specific context
3. Make names searchable - an agent should find the right code in one grep
4. Choose specificity over brevity - `calculateMonthlyRecurringRevenue()` beats `calcMRR()`

### Codebase Consistency Patterns
1. **Same Folder Structure**: Repeat patterns across modules (every service has models/, controllers/, tests/)
2. **Same Naming Patterns**: If one endpoint is `getUserById`, make it `getProductById`, not `fetchProduct`
3. **Same Code Style**: Use linting/formatting tools to enforce consistency
4. **Same Comment Structure**: Standardize docstrings, inline comments, and file headers
5. **Same Import Order**: Alphabetical, grouped by type (stdlib, third-party, local)

**Why Consistency Matters**: When your codebase grows to thousands of files, consistency allows agents to make reliable assumptions. Inconsistency forces agents to verify every assumption, wasting tokens and time.

## Coding principles
1. Use a style guide, so all the code looks relatively the same
2. Code is written for people, not just computers
3. Make modules easy to learn and understand
4. Go into everything with a plan
5. Shorter code is not necessarily better code. MAKE IT READABLE
6. Break up actions into methods

## Logging Standards for Agentic Operations
**CRITICAL**: Your agent can only see what gets printed to standard output. Comprehensive logging is not optional - it's the primary feedback mechanism that guides agents to successful problem resolution.

### The Standard Output Principle
**Your agent is brilliant but blind**: Without clear logging, agents cannot diagnose issues, track progress, or validate success. Every operation must communicate its state through standard output.

**Core Rule**: If you wouldn't be able to debug it without the logs, neither can your agent.

### Standard Output Requirements
1. **Always Print to stdout/stderr**: All application activity should produce visible output
2. **Structured Format**: Use consistent log formatting (timestamp, level, component, message)
3. **Agent-Readable**: Logs are consumed by AI agents, not just humans - be explicit and detailed
4. **Context Rich**: Include relevant identifiers (user IDs, transaction IDs, file paths, line numbers)
5. **Token Efficient**: Balance verbosity with context window limits - use session log files for high-volume apps

### Error Logging Patterns
**MANDATORY**: Log every exception with full context before bubbling up or returning error responses.

```python
# Python Example - Good Error Logging
try:
    result = process_transaction(transaction_id)
except ValidationError as e:
    print(f"ERROR [TransactionService]: Validation failed for transaction {transaction_id}: {str(e)}")
    raise
except DatabaseError as e:
    print(f"ERROR [TransactionService]: Database error processing transaction {transaction_id}: {str(e)}")
    raise
```

```typescript
// TypeScript Example - Good Error Logging
try {
    const result = await processTransaction(transactionId);
} catch (error) {
    console.error(`ERROR [TransactionService]: Failed to process transaction ${transactionId}:`, error);
    throw error;
}
```

**Error Log Requirements**:
1. **Error Type**: Log the exception/error class name
2. **Error Message**: Full error message with details
3. **Context**: What operation was being performed
4. **Identifiers**: Relevant IDs (user, transaction, resource)
5. **Stack Trace**: Include for unexpected errors (optional for validation errors)

### Success Logging Patterns
**Don't just log failures - log successes too**. Success logs help agents understand normal operation flow and confirm fixes.

```python
# Python Example - Good Success Logging
@app.post("/api/upload")
async def upload_data(file: UploadFile):
    print(f"INFO [UploadEndpoint]: Received file upload: {file.filename}")
    result = await process_upload(file)
    print(f"INFO [UploadEndpoint]: Successfully processed {file.filename} - {result.rows_inserted} rows inserted")
    return {"status": "success", "details": result}
```

```typescript
// TypeScript Example - Good Success Logging
app.post('/api/upload', async (req, res) => {
    console.log(`INFO [UploadEndpoint]: Received file upload: ${req.file.filename}`);
    const result = await processUpload(req.file);
    console.log(`INFO [UploadEndpoint]: Successfully processed ${req.file.filename} - ${result.rowsInserted} rows inserted`);
    res.json({ status: 'success', details: result });
});
```

**Success Log Requirements**:
1. **Operation Name**: What succeeded
2. **Key Metrics**: Rows processed, files created, time taken
3. **Identifiers**: Relevant IDs for traceability
4. **Confirmation**: Explicit "success" or "completed" language

### Log File Management
For applications that generate high log volume:

1. **Per-Session Log Files**: Create timestamped log files for each session/request
   ```python
   # Example: logs/session_20251017_143022.log
   log_file = f"logs/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
   ```

2. **Rotation Strategy**: Implement log rotation to prevent disk space issues
3. **Log Levels**: Support configurable log levels (DEBUG, INFO, WARNING, ERROR)
4. **Separation of Concerns**: Separate application logs from access logs from error logs

### Agent-Friendly Log Formatting
**Recommended Format**: `[LEVEL] [Component]: Message with {context}`

**Examples**:
```
INFO [AuthService]: User authentication successful for user_id=12345
ERROR [PaymentGateway]: Payment processing failed for transaction_id=tx_98765 - Invalid card number
WARNING [DatabaseConnection]: Connection pool at 90% capacity (45/50 connections)
DEBUG [CacheService]: Cache miss for key=user_profile_12345, fetching from database
```

**Why This Format Works**:
- **Level First**: Agents can quickly filter by severity
- **Component in Brackets**: Enables quick source identification
- **Structured Context**: Key-value pairs are easily parseable
- **Consistent Delimiters**: Colon separates component from message, equals signs for values

### Integration with Error Handling
Logging must integrate seamlessly with your error handling strategy:

1. **Log Before Throwing**: Always log context before raising exceptions
2. **Log at Boundaries**: Log at API endpoints, service entry points, and external integrations
3. **Correlation IDs**: Use request IDs to trace operations across services
4. **No Silent Failures**: Every error path must produce visible output

**Anti-Pattern to Avoid**:
```python
# BAD - Agent sees nothing
try:
    result = risky_operation()
    return result
except Exception:
    return {"error": "Operation failed"}
```

**Correct Pattern**:
```python
# GOOD - Agent sees full context
try:
    print(f"INFO [Service]: Starting risky_operation with params={params}")
    result = risky_operation()
    print(f"INFO [Service]: risky_operation completed successfully")
    return result
except Exception as e:
    print(f"ERROR [Service]: risky_operation failed with error: {str(e)}")
    print(f"ERROR [Service]: Stack trace: {traceback.format_exc()}")
    return {"error": "Operation failed", "details": str(e)}
```

## Deployment principles
1. Deployment should be built with the idea of retreat. If something goes wrong, there must be a way to revert. 
2. The most important step in deployment is having a plan to roll back


## Universal Development Workflow
1. Before making any changes, create and checkout a feature branch named `feature-[brief-description]`
2. Write comprehensive tests for all new functionality
3. Compile code and run all tests before committing
4. Write detailed commit messages explaining changes and rationale
5. Test new code and address issues before committing 
6. Commit all changes to the feature branch


## Enterprise Technology Stack (Company Standard)
- **Frontend**: React 18 + TypeScript + Vite + Material-UI
- **Backend**: FastAPI + Python 3.11 + PostgreSQL + SQLAlchemy 2.0
- **Code Quality**: Biome linting, comprehensive type safety
- **State Management**: useReducer for complex state, Context API for global state
- **Forms**: Mandatory react-hook-form with Material-UI integration
- **Authentication**: JWT with role-based access control

## Code Standards
- **Component Naming**: All form/business components must start with FK prefix (e.g., `FKUserForm.tsx`)
- **Information-Dense Keywords (IDK)**: Use meaningful, searchable names for all types, classes, functions, and variables (avoid generic terms like "data", "handler", "utils" without context)
- **File Size Limits**: Soft limit of 1000 lines per file for optimal maintainability and agent processing
- **Type Traceability**: Types, classes, and interfaces should trace clear information flows through the application
- **TypeScript**: 100% coverage, no `any` types in production code
- **Backend**: Type hints for all functions, comprehensive docstrings, Clean Architecture
- **External APIs**: Secure integration with proper authentication and error handling
- **Documentation**: All public APIs documented with examples

## Enterprise Project Structure

### Frontend Architecture
```
src/
├── main.tsx                  # ENTRY POINT - Application bootstrap
├── App.tsx                   # Root component
├── api/clients/              # HTTP clients with interceptors
├── components/forms/         # FK-prefixed form components
├── components/ui/            # FK-prefixed reusable components
├── hooks/                    # Custom hooks (useAuth, useAPI, etc.)
├── store/reducers/           # useReducer implementations
├── services/                 # Business logic services
├── types/                    # TypeScript interfaces and domain models
├── utils/                    # Utility functions
├── pages/                    # Application routes
└── README.md                 # Frontend documentation
```

**Note**: Each major subsystem should include its own README.md or CLAUDE.md for agent navigation.

### Backend Architecture
```
src/
├── main.py                   # ENTRY POINT - Application startup
├── adapter/rest/             # FastAPI controllers and routes
├── core/servicess/           # Business logic services
├── repository/               # Data access layer with docstrings
├── interface/                # DTOs and contracts
├── models/                   # SQLAlchemy models
├── config/                   # Application configuration
└── README.md                 # Backend documentation

tests/                        # SYNCHRONIZED STRUCTURE with src/
├── adapter/                  # Tests for adapters
├── core/                     # Tests for core services
└── repositorio/              # Tests for repositories
```

**Critical**: Test directory structure must mirror application structure for easy agent navigation and test discovery.

## Quality Standards (Non-negotiable)
- **Testing**: Comprehensive test coverage for business logic
- **Security**: JWT authentication, input validation, SQL injection prevention
- **Performance**: API responses optimized, proper indexing
- **Code Quality**: Biome linting pass, no critical security vulnerabilities
- **Error Handling**: Structured exceptions with proper HTTP status codes

## Enterprise Patterns (Mandatory)
- **Clean Architecture**: Clear separation of concerns
- **External APIs**: Circuit breaker pattern with retry logic
- **Monitoring**: Structured logging with correlation IDs
- **Security**: CORS configuration and rate limiting
- **Deployment**: Docker containers with environment-specific configs

## MVP Development Approach
While maintaining enterprise standards, MVPs should:
- **Start Simple**: Core functionality first, advanced features later
- **Iterate Fast**: Quick deployment cycles for user feedback
- **Scale Ready**: Built on enterprise foundation for easy scaling
- **Maintain Quality**: No technical debt that violates core principles

## Project Extensions
Each project's `claude.md` should extend this base with:
- Specific business domain models
- Feature requirements and user stories
- API endpoint specifications
- Database schema definitions
- Deployment and environment configs
- Project-specific validation rules

## Command Files and Scripts

### Available Commands
```bash
# Development
npm install          # Install dependencies
npm run dev          # Start development server (Vite with HMR)
npm run build        # Build for production (TypeScript check + Vite build)
npm run preview      # Preview production build locally
npm run lint         # Run ESLint with TypeScript rules
npm run typecheck    # Run TypeScript type checking
npm run clean        # Clean build artifacts and dependencies
npm run clean:cache  # Clean Vite cache
npm run format       # Format code with Prettier (needs prettier installed)
```

### Command File Locations
1. **scripts/** - Directory for custom shell/PowerShell scripts
2. **package.json** - npm scripts for common tasks
3. **Makefile** - Cross-platform commands (use `make help` to see all)
4. **.vscode/tasks.json** - VS Code integrated tasks

### Using Make Commands
```bash
make help       # Show all available commands
make dev        # Start development server
make build      # Build for production
make lint       # Run linting
make typecheck  # Run TypeScript type checking
```


## UI Design System

### Colors (Custom Tailwind Config)
- Primary: #050A53, #0C147B, #3C47D3, #77A1E2
- Coral/CTA: #EB8774, #F19F90
- Success: #E0F7E6/#2CA14D
- Error: #FFE4E4/#CC071E

### Component Standards
- Buttons: 52px(L)/44px(M)/36px(S), 8px radius
- Cards: 8px radius, 24px padding
- Inputs: 48px height, 8px radius
- Font: Epilogue (400, 500, 600, 700)

### Responsive Breakpoints
- Mobile: < 720px
- Tablet: 720px - 1024px
- Desktop: > 1024px

## Language Guidelines
- **UI Text**: Spanish (all user-facing content)
- **Code**: English (variables, functions, comments)
- **Documentation**: Spanish for user docs, English and Spanish for technical docs
- Please make sure the requirements contain all dependencies required for render to deploy
- when outputting jason, remember to  automatically converts datetime objects to ISO format strings for JSON serialization
- when documenting sessions, use this naming convention [YEAR][MONTH][DAY]_[NAME]. An example name would be 20251012_integral_analysis

## References and Additional Context

### Tactical Agentic Coding (TAC) Principles
The "Agentic Code Architecture Principles" and "Logging Standards for Agentic Operations" sections are based on Tactical Agentic Coding methodologies (TAC Lesson 2), which emphasize building codebases that AI agents can navigate and operate autonomously.

**Core Concept**: Agents are brilliant but ephemeral - they start each session with zero context. Architecture and logging are critical "through-agent leverage points" that determine how effectively agents can perform engineering work.

**The 12 Leverage Points of Agentic Coding**:
- **In-Agent (Core Four)**: Context, Model, Prompt, Tools
- **Through-Agent**: Standard Output, Documentation, Tests, Architecture, Types, Plans, Templates, ADRs (Architecture Decision Records)

**Related Documentation**: See `Transcripts/1760693062588-TAC-LESSON-2-mp3-bc2494ed-ac76.docx` for full context on tactical agentic coding principles.
- when documenting after doing code, add "postchange" in the file name