# 🚀 ProManage - Sistema de Gestión de Proyectos

Sistema completo de gestión de proyectos desarrollado desde cero con **FastAPI + React + Docker** siguiendo arquitectura de microservicios.

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![React](https://img.shields.io/badge/React-18.0-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-purple)

## 📋 Descripción del Proyecto

ProManage es un sistema de gestión de proyectos empresariales que implementa una **arquitectura de microservicios** con las siguientes características:

- ✅ **Backend FastAPI** con autenticación JWT y validación Pydantic 2.x
- ✅ **Frontend React** con Tailwind CSS y gestión de estado moderna
- ✅ **Base de datos PostgreSQL** con Redis para cache
- ✅ **Containerización completa** con Docker y Docker Compose
- ✅ **Control de roles** (Admin, Manager, User) con permisos granulares
- ✅ **API RESTful documentada** con Swagger UI automático

## 🏗️ Arquitectura Implementada

Frontend (React + Tailwind)     Backend (FastAPI + Pydantic)
Port 3000              ←→        Port 8000
│                                │
└────── HTTP/JSON API ──────────┘
│
▼
┌─────────────────────────────────┐
│         Docker Network          │
│  ┌─────────────┐ ┌────────────┐ │
│  │ PostgreSQL  │ │   Redis    │ │
│  │  Port 5432  │ │ Port 6379  │ │
│  └─────────────┘ └────────────┘ │
└─────────────────────────────────┘