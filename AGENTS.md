# Compliance Rules

This file contains the compliance and code quality rules for this repository.

## 1. Python Functions Must Include Type Annotations

**Objective:** Ensure type safety and improve code maintainability by requiring explicit type annotations for all function parameters and return values in Python code, as enforced by basedpyright type checking

**Success Criteria:** All Python function definitions include type hints for parameters and return types using Python 3.12+ syntax (e.g., list[str] instead of List[str], int | None instead of Optional[int])

**Failure Criteria:** Python function definitions lack type annotations for parameters or return values

---

## 2. Python Code Must Follow Ruff Linting Rules

**Objective:** Maintain consistent code quality and style by adhering to the project's ruff configuration, which enforces rules for code formatting, import ordering, security checks, and best practices

**Success Criteria:** All Python code passes ruff format and ruff check --fix without errors, following the rules defined in .ruff.toml including line length of 120 characters, proper import sorting, and security rules (S102, S307, S301, S302, S311)

**Failure Criteria:** Python code violates ruff linting rules such as improper formatting, incorrect import ordering, use of print() instead of logging, or security violations like using exec/eval/pickle

---

## 3. Backend Code Must Use Logging Instead of Print Statements

**Objective:** Enable proper observability and debugging by requiring all output to use the logging module rather than print statements, with logger instances declared at module level

**Success Criteria:** All logging is performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements in production code (tests are exempt)

**Failure Criteria:** Code contains print() statements outside of test files, or logging is performed without proper logger initialization

---

## 4. Python Code Must Use Modern Type Syntax for Python 3.12+

**Objective:** Leverage modern Python type system features for better code clarity and type safety by using the latest type annotation syntax

**Success Criteria:** Type annotations use Python 3.12+ syntax: list[T] instead of List[T], dict[K,V] instead of Dict[K,V], int | None instead of Optional[int], and str | int instead of Union[str, int]

**Failure Criteria:** Code uses legacy typing imports like List, Dict, Optional, Union from the typing module when modern syntax is available

---

## 5. Python Backend Files Must Not Exceed 800 Lines

**Objective:** Maintain code readability and modularity by keeping individual Python files under 800 lines, promoting proper code organization and separation of concerns

**Success Criteria:** All Python files in the backend (api/) contain fewer than 800 lines of code

**Failure Criteria:** Python files in the backend exceed 800 lines and should be split into multiple files

---

## 6. SQLAlchemy Sessions Must Use Context Managers

**Objective:** Ensure proper database connection management and prevent resource leaks by requiring all SQLAlchemy sessions to be opened with context managers

**Success Criteria:** All database operations use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for session management

**Failure Criteria:** Database sessions are created without context managers or sessions are not properly closed

---

## 7. Database Queries Must Include tenant_id Scoping

**Objective:** Ensure data isolation and security in multi-tenant architecture by requiring all database queries to be scoped by tenant_id to prevent cross-tenant data access

**Success Criteria:** All database queries that access tenant-scoped resources include WHERE clauses filtering by tenant_id

**Failure Criteria:** Database queries access tenant-scoped tables without tenant_id filtering, creating potential data leakage

---

## 8. Python Tests Must Follow pytest AAA Pattern

**Objective:** Maintain clear and maintainable test structure by requiring all pytest tests to follow the Arrange-Act-Assert pattern for better readability and understanding

**Success Criteria:** Test functions are structured with three distinct sections: Arrange (setup), Act (execution), Assert (verification), with clear separation between phases

**Failure Criteria:** Test functions mix setup, execution, and assertion logic without clear separation or organization

---

## 9. TypeScript Must Avoid any Type Annotations

**Objective:** Maintain type safety in the frontend codebase by avoiding the any type, which bypasses TypeScript's type checking and can lead to runtime errors

**Success Criteria:** TypeScript code uses specific types or unknown instead of any, with ts/no-explicit-any warnings addressed

**Failure Criteria:** Code contains 'any' type annotations without justified exceptions or proper type definitions

---

## 10. TypeScript Must Use Type Definitions Instead of Interfaces

**Objective:** Maintain consistency in type declarations across the codebase by preferring type definitions over interfaces, as enforced by ts/consistent-type-definitions rule

**Success Criteria:** All TypeScript type declarations use 'type' keyword instead of 'interface' keyword, following the pattern: type MyType = { ... }

**Failure Criteria:** Code uses 'interface' declarations instead of 'type' definitions

---

## 11. Frontend User-Facing Strings Must Use i18n Translations

**Objective:** Enable internationalization and localization by requiring all user-facing text in the frontend to be retrieved from i18n translation files rather than hardcoded

**Success Criteria:** All user-facing strings are defined in web/i18n/en-US/ translation files and accessed via useTranslation hook with proper namespace options, following dify-i18n/require-ns-option rule

**Failure Criteria:** User-facing strings are hardcoded in component files instead of using translation keys

---

## 12. TypeScript Files Must Follow Strict TypeScript Configuration

**Objective:** Ensure type safety and catch potential errors at compile time by enabling strict TypeScript compiler options

**Success Criteria:** All TypeScript code compiles successfully with strict mode enabled in tsconfig.json, including strict type checking and consistent casing enforcement

**Failure Criteria:** Code contains type errors or inconsistent casing that would fail strict TypeScript compilation

---

## 13. Backend Configuration Must Be Accessed via configs Module

**Objective:** Centralize configuration management and prevent direct environment variable access by requiring all configuration to be retrieved through the configs module

**Success Criteria:** Configuration values are accessed through configs.dify_config or related config modules, not via direct os.environ or os.getenv calls

**Failure Criteria:** Code directly reads environment variables using os.environ or os.getenv instead of using the configs module

---

## 14. Python Backend Must Use Pydantic v2 for Data Validation

**Objective:** Ensure consistent data validation and serialization using Pydantic v2 models with proper configuration for DTOs and request/response validation

**Success Criteria:** All data transfer objects use Pydantic v2 BaseModel with ConfigDict(extra='forbid') by default, and use @field_validator/@model_validator for domain rules

**Failure Criteria:** Data validation uses Pydantic v1 syntax, allows undeclared fields without explicit configuration, or uses custom validation logic instead of Pydantic validators

---

## 15. Backend Errors Must Use Domain-Specific Exceptions

**Objective:** Provide clear error handling and appropriate HTTP responses by raising domain-specific exceptions from services and translating them to HTTP responses in controllers

**Success Criteria:** Business logic raises exceptions from services/errors or core/errors modules, and controllers handle these exceptions to return appropriate HTTP responses

**Failure Criteria:** Services return HTTP responses directly, or generic exceptions are raised without domain context

---

## 16. Python Code Must Use Snake Case for Variables and Functions

**Objective:** Maintain consistent naming conventions across the Python codebase by using snake_case for variables and functions, PascalCase for classes, and UPPER_CASE for constants

**Success Criteria:** All Python variables and functions use snake_case naming (e.g., user_name, get_user_data), classes use PascalCase (e.g., UserService), and constants use UPPER_CASE (e.g., MAX_RETRIES)

**Failure Criteria:** Python code uses camelCase, PascalCase for variables/functions, or inconsistent naming patterns

---

## 17. Frontend ESLint Sonarjs Rules Must Be Followed

**Objective:** Maintain code quality and prevent common bugs by adhering to SonarJS cognitive complexity and maintainability rules configured in the project

**Success Criteria:** TypeScript code passes SonarJS linting rules including no-dead-store (error level), max-lines warnings (1000 line limit), and no-variable-usage-before-declaration (error level)

**Failure Criteria:** Code violates SonarJS rules such as dead stores, files exceeding 1000 lines, or variables used before declaration

---

## 18. Backend Architecture Must Follow Import Layer Constraints

**Objective:** Maintain clean architecture boundaries by enforcing layer separation through import-linter rules that prevent circular dependencies and upward imports

**Success Criteria:** Code adheres to import-linter contracts defined in .importlinter, including workflow layer separation (graph_engine → graph → nodes → entities) and domain isolation rules

**Failure Criteria:** Imports violate architectural layers by importing from higher layers or creating circular dependencies not explicitly allowed in .importlinter

---

## 19. Backend Storage Access Must Use Abstraction Layer

**Objective:** Ensure consistent and secure storage operations by requiring all storage access to go through extensions.ext_storage.storage abstraction

**Success Criteria:** All file storage operations use extensions.ext_storage.storage interface instead of direct filesystem or cloud storage APIs

**Failure Criteria:** Code directly accesses filesystem, S3, Azure Blob, or other storage without using the storage abstraction layer

---

## 20. Backend HTTP Requests Must Use SSRF Proxy Helper

**Objective:** Prevent Server-Side Request Forgery attacks by requiring all outbound HTTP requests to use the SSRF proxy helper for validation and protection

**Success Criteria:** All outbound HTTP fetches use core.helper.ssrf_proxy instead of direct httpx, requests, or urllib calls

**Failure Criteria:** Code makes outbound HTTP requests without using the SSRF proxy helper, potentially exposing internal resources

---

## 21. Python Code Must Not Override Dunder Methods Unnecessarily

**Objective:** Prevent subtle bugs and maintain expected Python object behavior by avoiding unnecessary overrides of special methods like __init__, __iadd__, etc.

**Success Criteria:** Special methods (__init__, __iadd__, __str__, __repr__) are only overridden when necessary with proper implementation of relevant special methods documented in coding_style.md

**Failure Criteria:** Code overrides dunder methods without clear justification or without implementing complementary methods

---

## 22. Backend Must Avoid Security-Risky Functions

**Objective:** Prevent remote code execution vulnerabilities by prohibiting the use of dangerous built-in functions that can execute arbitrary code

**Success Criteria:** Python code does not use exec(), eval(), pickle, marshal, or ast.literal_eval() as enforced by ruff security rules S102, S307, S301, S302

**Failure Criteria:** Code uses exec(), eval(), pickle.loads(), marshal.loads(), or ast.literal_eval() which can execute arbitrary code

---

## 23. Python Backend Must Use Deterministic Control Flow

**Objective:** Optimize for observability and debugging by maintaining deterministic control flow with clear logging and actionable errors

**Success Criteria:** Code avoids clever hacks, maintains readable control flow, includes tenant/app/workflow identifiers in log context, and logs retryable events at warning level and terminal failures at error level

**Failure Criteria:** Code uses obfuscated logic, lacks proper logging context, or mixes logging levels inappropriately

---

## 24. Backend Async Tasks Must Be Idempotent

**Objective:** Ensure reliability of background processing by requiring all async tasks to be idempotent and log relevant object identifiers for debugging

**Success Criteria:** All background tasks in tasks/ are idempotent (can be safely retried), log the relevant object identifiers (tenant_id, app_id, etc.), and specify explicit queue selection

**Failure Criteria:** Background tasks are not idempotent, lack proper logging identifiers, or don't specify queue configuration

---

## 25. Frontend Code Must Not Use console Statements

**Objective:** Prevent debug code from reaching production by treating console statements as warnings that should be removed or replaced with proper logging

**Success Criteria:** Production frontend code avoids console.log, console.warn, console.error statements as enforced by no-console warning rule

**Failure Criteria:** Code contains console statements that should be removed or replaced with proper logging mechanisms

---
