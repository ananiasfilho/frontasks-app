# Frontasks (macOS) — Checklist de QA manual

> App nativo com muito comportamento dependente de contexto (janela, Spaces, login,
> instalação). Não há testes automatizados de UI, então rode este roteiro antes de
> cada release.

## Núcleo (CRUD)
- [ ] Criar tarefa (Enter no campo "Nova tarefa")
- [ ] Editar título inline; digitar rápido não trava nem perde caracteres (debounce)
- [ ] Esvaziar o título e confirmar (Enter ou clicar fora) → a tarefa é apagada
- [ ] Concluir / desconcluir (checkbox) — risco + opacidade
- [ ] Apagar (hover → lixeira)
- [ ] Menu de contexto (botão direito na tarefa): Concluir/Reabrir e Apagar
- [ ] Reordenar arrastando; a ordem persiste após reabrir
- [ ] Limpar concluídas (borracha no cabeçalho)

## Janela / multi-tela
- [ ] Fica sempre no topo, sobre apps normais
- [ ] Não rouba o foco (dá pra continuar digitando no app de baixo)
- [ ] Redimensionar; reabre no mesmo tamanho/posição
- [ ] 1ª vez (sem posição salva): canto superior direito do **monitor central**
- [ ] Aparece em todos os Spaces
- [ ] Multi-monitor: posição correta com 1, 2 e 3 telas

## Atalho global
- [ ] ⌥Espaço mostra/oculta de qualquer app
- [ ] Se o atalho já estiver em uso por outro app: Ajustes mostra **"indisponível"**
      e a barra de menus continua funcionando (fallback)

## Persistência
- [ ] Fechar e reabrir mantém as tarefas
- [ ] Editar um título e **sair imediatamente** (< 0,5s) NÃO perde a edição (flush no encerrar)
- [ ] `tasks.json` inválido/corrompido: app abre sem crashar; erro visível no Console
- [ ] Pasta sem permissão de escrita: erro é logado, app não trava

## Ajustes
- [ ] Cores (destaque, fundo + transparência, texto), fonte e tamanho aplicam ao vivo
- [ ] "Iniciar ao ligar o Mac": liga/desliga e o toggle reflete o estado real do sistema
- [ ] Reiniciar a sessão do macOS com o login ligado → app sobe sozinho

## Instalação / distribuição
- [ ] DMG: arrastar para Applications, abrir (liberar quarentena na 1ª vez)
- [ ] `brew install --cask ananiasfilho/tap/frontasks`
- [ ] Rodar de **dentro** e de **fora** de `/Applications`
- [ ] 1ª abertura: aviso do Gatekeeper + liberação (`xattr` ou Ajustes do Sistema)

---

## Fase futura — piso do macOS (decisão em aberto)

Hoje `LSMinimumSystemVersion = 15.0` (macOS 15). Para **baixar o piso** (ex.: 14 Sonoma
ou 13 Ventura) e alcançar mais usuários, é preciso **testar numa VM** antes — o
ambiente de dev só tem o macOS mais novo.

- **Ferramenta (Apple Silicon):** usar **UTM** (grátis, baseado no *Virtualization
  framework* da Apple) ou o CLI **tart**. ⚠️ **VirtualBox NÃO roda macOS como guest**
  em Apple Silicon — não é opção.
- **Passos:** baixar o IPSW do macOS alvo (14/13), criar a VM, instalar o `.app` e
  rodar este checklist inteiro. Passando, baixar `.macOS("14")` (ou 13) no
  `Package.swift`, o `LSMinimumSystemVersion` no `make-app.sh` e o `depends_on macos:`
  no cask do Homebrew.
