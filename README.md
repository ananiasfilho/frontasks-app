# Frontasks

**Lista de tarefas flutuante e sempre-no-topo — leve, redimensionável e discreta.**

Frontasks é um painel de tarefas que fica *sobre* os outros apps, sempre à vista, sem roubar o foco do que você está fazendo. Sem ícone no Dock/barra de tarefas: só as suas tarefas, num cartão translúcido que você posiciona e dimensiona como quiser.

<p align="center">
  <img src="macos/docs/panel.png" alt="Frontasks" width="300">
</p>

<p align="center">
  <img alt="Licença: AGPL v3" src="https://img.shields.io/badge/license-AGPL--3.0-green">
  <img alt="macOS 15+"        src="https://img.shields.io/badge/macOS-15%2B-black?logo=apple">
  <img alt="Linux (WIP)"      src="https://img.shields.io/badge/Linux-em%20desenvolvimento-orange?logo=linux&logoColor=white">
</p>

---

## 🖥️ Plataformas

| Plataforma | Status | Onde |
|---|---|---|
| **macOS** (SwiftUI + AppKit) | ✅ **Disponível** — v0.1.0 | [`macos/`](macos/) · [**Baixar (Releases)**](https://github.com/ananiasfilho/frontasks-app/releases) |
| **Linux** (GTK3, foco Mint Cinnamon) | 🚧 **Em desenvolvimento** | [`linux/`](linux/) |

Este é um **monorepo**: cada plataforma tem sua pasta, com implementação nativa e
compatibilidade de dados (mesmo formato de tarefas e preferências).

## ✨ Recursos

- **Sempre no topo**, redimensionável, sem roubar o foco
- Criar, editar, concluir, apagar · **reordenar** arrastando · **limpar concluídas**
- **Atalho global** para mostrar/ocultar
- **Personalização**: cor de destaque, cor de fundo + transparência, cor do texto, fonte e tamanho
- **Iniciar no login** · discreto (fora do Dock/barra de tarefas, só na bandeja/menu)

## 🖼️ Telas (macOS)

<p align="center">
  <img src="macos/docs/panel.png" alt="Painel" width="280">
  &nbsp;&nbsp;
  <img src="macos/docs/settings.png" alt="Ajustes" width="280">
</p>

<p align="center">
  <img src="macos/docs/theme-blue.png" alt="Tema azul" width="200">
  <img src="macos/docs/theme-red.png"  alt="Tema vermelho" width="200">
  <img src="macos/docs/panel.png"      alt="Tema roxo" width="200">
</p>

## 🚀 Começando

- **macOS:** baixe o `.dmg` em [Releases](https://github.com/ananiasfilho/frontasks-app/releases)
  e arraste para Applications — ou compile do código em [`macos/`](macos/) (sem Xcode, via SwiftPM).
- **Linux:** veja o guia de desenvolvimento em [`linux/`](linux/).

## 📄 Licença

**GNU Affero General Public License v3.0** (AGPL-3.0). Veja [LICENSE](LICENSE).

> Copyright (C) 2026 Ananias Filho
