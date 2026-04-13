# Render Deploy Guide

## 1) Voraussetzungen

- Repository ist mit Render verbunden.
- Service-Typ: **Web Service**
- Runtime: **Docker**

## 2) Konfiguration in Render

- **Branch**: gewünschter Deploy-Branch
- **Auto-Deploy**: aktiviert (empfohlen)
- **Health Check Path**: `/`

## 3) Startverhalten

Der Container startet den Server mit:

- Host: `0.0.0.0`
- Port: `${PORT}` (Render setzt diese Variable automatisch)

## 4) Erster Test nach Deploy

- Service-URL in Render öffnen.
- UI muss erreichbar sein (Startseite `/`).
- API-Stichprobe: `/api/meta`
