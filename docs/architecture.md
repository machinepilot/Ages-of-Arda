# Brogue DM Agent Architecture

## System Overview

The Brogue DM Agent is a modular system that enhances the Brogue game experience
by providing intelligent, contextual narrative elements powered by Ollama3.

## Component Diagram

```mermaid
graph TD
    A[Brogue Game] <--> B[C99 MCP Client]
    B <--> C[MCP Gateway]
    C <--> D[Core Service]
    D <--> E[Memory Service]
    D <--> F[Narrative Service]
    F <--> G[Ollama Service]
    E <--> H[( 