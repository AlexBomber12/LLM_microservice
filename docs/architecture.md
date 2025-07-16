# Architecture

```plantuml
@startuml
actor Client
package "LLM Microservice" {
  [FastAPI Server] --> [vLLM Engine]
}
Client --> [FastAPI Server]
@enduml
```
