# FronTasks (Linux) — Checklist de QA manual

> App GTK3 com muito comportamento dependente de contexto (janela, workspaces,
> login, instalação, compositor). Não há testes automatizados de UI, então rode
> este roteiro antes de cada release. Ambiente-alvo: **X11 / Cinnamon** (Linux
> Mint). Wayland limita atalho global e always-on-top — testar à parte.

## Núcleo (CRUD)
- [ ] Criar tarefa (Enter no campo "Nova tarefa")
- [ ] Editar título inline (clique no texto); digitar rápido não trava nem perde caracteres
- [ ] Esvaziar o título e confirmar (Enter ou clicar fora) → a tarefa é apagada
- [ ] Concluir / desconcluir (checkbox) — risco + opacidade
- [ ] Apagar (hover → ✕)
- [ ] Menu de contexto (botão direito na tarefa): Concluir/Reabrir e Apagar
- [ ] Reordenar arrastando pelo grip (⠿); soltar na metade de baixo insere DEPOIS;
      a ordem persiste após reabrir
- [ ] Limpar concluídas (⌫ no cabeçalho) — só aparece quando há concluídas

## Janela / multi-tela
- [ ] Fica sempre no topo, sobre apps normais
- [ ] Não rouba o foco (dá pra continuar digitando no app de baixo ao mostrar pelo
      atalho/bandeja)
- [ ] Arrastar pelo cabeçalho move a janela; clicar nos botões (⌫/⚙) NÃO move
- [ ] Redimensionar pelas bordas/cantos; respeita o mínimo (240×200);
      reabre no mesmo tamanho/posição
- [ ] 1ª vez (sem geometria salva): canto superior direito do **monitor central**
- [ ] Aparece em todos os workspaces (stick)
- [ ] Multi-monitor: posição correta com 1, 2 e 3 telas
- [ ] Geometria salva que caiu fora da tela (monitor removido/resolução mudou):
      reabre no canto superior direito em vez de invisível
- [ ] Sem compositor (Muffin desligado): degrada sem transparência, não trava

## Atalho global
- [ ] O atalho configurado mostra/oculta de qualquer app
- [ ] Se o registro falhar (em uso, ou Wayland): Ajustes mostra **"⚠ Não registrado"**
      e a bandeja continua funcionando (fallback)
- [ ] Trocar o atalho em `settings.json` e reiniciar aplica o novo

## Persistência
- [ ] Fechar e reabrir mantém as tarefas
- [ ] Editar um título e sair imediatamente NÃO perde a edição (escrita atômica)
- [ ] `tasks.json` inválido/corrompido: app abre sem crashar; o arquivo ruim vira
      `tasks.json.corrupt-<timestamp>`; erro logado no stderr
- [ ] `settings.json` com valores fora de tipo/faixa: cai pros defaults sem crashar
- [ ] `geometry.json` inválido: ignora e usa posição inicial
- [ ] Pasta sem permissão de escrita: erro é logado, app não trava
- [ ] `XDG_CONFIG_HOME` customizado: config, tasks e autostart vão pra lá

## Bandeja (tray)
- [ ] Ícone aparece na bandeja (XApp.StatusIcon no Cinnamon; StatusNotifier no GNOME
      com extensão de indicador)
- [ ] Clique esquerdo alterna o painel
- [ ] Clique direito abre o menu (Mostrar/ocultar, Ajustes, Sair)
- [ ] Sem entrada na barra de tarefas

## Ajustes
- [ ] Cores (destaque, fundo + transparência, texto) e fonte/tamanho aplicam ao vivo
- [ ] Slider de opacidade/tamanho não trava a janela (debounce); tamanho salva inteiro
- [ ] "Iniciar ao ligar o computador": liga/desliga e cria/remove o `.desktop` em
      `autostart/`; se a escrita falhar, o checkbox reverte
- [ ] Reiniciar a sessão com autostart ligado → app sobe sozinho

## Instalação / distribuição
- [ ] `.deb`: `sudo apt install ./frontasks_*.deb` resolve as dependências
      (python3-gi, gir1.2-gtk-3.0, gir1.2-keybinder-3.0, gir1.2-xapp-1.0)
- [ ] `.rpm`: `sudo dnf install ./frontasks-*.rpm` resolve (python3-gobject, gtk3,
      keybinder3, xapps)
- [ ] Comando `frontasks` no PATH após instalar
- [ ] `.desktop` de lançador aparece no menu de aplicativos com ícone
- [ ] Rodar via pacote NÃO copia ícone pra `~/.local/share/icons` (sem resíduo);
      rodar de dev (checkout) copia pra bandeja funcionar
- [ ] Segunda invocação de `frontasks` alterna a instância existente (single-instance)

## Ambientes testados (registrar aqui a cada rodada)
- [ ] Linux Mint / Cinnamon / X11 (alvo principal)
- [ ] Ubuntu (GNOME) — bandeja nativa
- [ ] Debian (GNOME) — bandeja depende de extensão de indicador
- [ ] Fedora (GNOME) — idem
