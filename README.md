# BastionAI: Secure Infrastructure for AI Brands
**Designed for professional agents, built for data sovereignty.**

**BastionAI provides a robust, multi-tenant foundation for businesses looking to deploy proprietary AI agents with complete control. We simplify the complexities of LLM integration and deployment, replacing them with a privacy-first architecture—utilizing Postgres Row-Level Security (RLS) for logical data isolation and transparent, auditable code.**

*Built in alignment with European standards for privacy and data protection, BastionAI allows you to scale your AI brand on a reliable, secure, and sovereign foundation.*

## Description
A modular, containerized platform designed to provide a branded, secure, and multi-tenant wrapper for LLM services. The architecture enables businesses to deploy proprietary AI agents with integrated subscription billing and usage management, ensuring data isolation and enterprise-grade security.

## Infrastructure & Environment
- **Target OS:** Linux-based distributions (optimized for AlmaLinux, Ubuntu, or Debian).
- **Resource Footprint:** Efficiently optimized for 2 vCPUs and 2GB RAM; deployment-ready via containerized environments.
- **Security Architecture:**
  - Encrypted storage volumes via LUKS.
  - Multi-tenant architecture enforced by Postgres Row-Level Security (RLS), ensuring strict logical isolation of proprietary agent training data.
  - Web serving and automated TLS via Caddy.


## Technology Stack
### Backend
- **Framework:** Python, FastAPI, and Uvicorn.
- **Data Management:** PostgreSQL with pgvector extension for RAG (Retrieval-Augmented Generation) capabilities and SQLAlchemy ORM.
- **Integration Layer:** LiteLLM for unified LLM provider abstraction (Anthropic/OpenAI) and Stripe SDK for subscription lifecycle management.
- **Security Utilities:** Native bcrypt for secure credential handling.

### Frontend
- **Framework:** React and Vite, focused on a modular, personalized interface.

## Core Features
- **Multi-Tenancy:** Hardened tenant isolation via RLS policies, preventing cross-tenant data leakage at the database kernel level.
- **Usage Tracking:** Token-based consumption monitoring to support scalable monthly subscription models.
- **Deployment:** Container-first architecture using Podman for reproducible development and production parity.

## Design Principles
- **Privacy-First by Design:** We believe data sovereignty is non-negotiable. By leveraging Postgres Row-Level Security and local-first data processing, we ensure that sensitive agent training data remains cryptographically and logically isolated from the platform core.
- **Open-Source Ethics:** We provide transparent, BSD-3 licensed code to foster community trust. We believe that critical AI infrastructure should be auditable, avoiding the "black box" risks common in modern AI SaaS.
- **Production-Grade Stability:** We prioritize predictable, containerized deployments and rigorous architectural patterns. Our goal is to provide a reliable, maintainable foundation that allows businesses to scale their AI brands with confidence.


**Development Methodology:** This project utilizes AI-assisted coding to accelerate implementation and ensure robust, production-grade standards through iterative, human-vetted engineering.

**Built for:** Organizations that value data ownership, architectural transparency, and the peace of mind that comes with human-vetted AI infrastructure.

**LEGAL NOTICE:** The platform core (backend and frontend) is distributed under the **BSD-3-Clause License**. All agent-specific training data and proprietary RAG assets remain strictly confidential and the **exclusive property** of the end-user/tenant.
