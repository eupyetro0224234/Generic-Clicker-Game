# Generic Clicker Game

[![Projeto no Itch.io][![Projeto no Itch.io](https://i.postimg.cc/hPsCTZ9m/image.png)](https://eupyetro022.itch.io/generic-clicker-game) ![Badge de versão](https://img.shields.io/badge/version-0.0.06-yellow) ![Licença Proprietária Customizada](https://img.shields.io/badge/license-Proprietária%20Customizada-blue)

**Desative o tradutor do seu navegador ao ler**

> _Esse projeto foi criado para eu começar a aprender Python com ajuda de ia. Com alguns projetos anteriores, usei o meu conhecimento extremamente básico e decidi dar vida ao projeto Generic Clicker Game._

---
## Sumário

- [Sobre a mudança de nome](#sobre-a-mudanca-de-nome)
- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Contribuições](#contribuições)
- [Mods](#mods)
- [Questões Comuns](#questões-comuns)
- [Envie suas sugestões e contribuições](#envie-suas-sugestões-e-contribuições)
- [Licença Customizada](#licença-customizada)
- [Contato](#contato)
- [Créditos](#créditos)
- [Changelogs](#changelogs)
---

## Sobre a mudança de nome

Eu acho Just Another Generic Clicker Game, But With References um nome gigante. Eu tentei criar diversas contas em vários aplicativos pra poder usar esse nome, por exemplo na página do twitter. Não consegui até agora pensar em nenhuma abreviação decente. JAGCMBWR? Isso não soa bem muito menos prático como apenas GCG ou se preferir, Generic Clicker Game. Como usei acima o exemplo do twitter, eu posso usar como se fosse um clã (viajei longe agora), por exemplo, GCG - eupyetro022. Por isso, eu decidi mudar o nome. Mas, o nome Just Another Generic Clicker Game, But With References pode ser utilizado pra algo no futuro...

## Sobre

Este é um jogo clicker feito em Python com Pygame, inspirado em jogos como Cookie Clicker. A ideia é simples: clicar, ganhar pontos e desbloquear upgrades e conquistas.

O projeto foi criado como um experimento pessoal para aprender desenvolvimento de jogos. Apesar do estilo descontraído e meio “meme”, ele foi feito com bastante cuidado (um meme levado a sério).

---

## Funcionalidades

✅ **Clique para ganhar pontos**

✅ **Sistema de upgrades**

✅ **Sistema de conquistas**

✅ **Menus interativos**

✅ **Efeitos visuais de clique**

✅ **Salvamento automático de progresso** 

✅ **Interface responsiva e estilizada**

---

## Instalação

Siga os passos abaixo para rodar o projeto localmente (caso prefira, vá em [releases](https://github.com/eupyetro0224234/Generic-CLicker-Game/releases) e baixe o executável mais recente):

<span style="font-size:22px; color:red;"><b><i>Certifique-se de ter pelo menos o Python 3.11 instalado (recomendo o 3.11.9, mas até a versão 3.13.7 está tudo funcionando perfeitamente), a versão mais recente do Git e algum editor de códigos (recomendo o Visual Studio Code).</i></b></span>


Clone o repositório
```bash
git clone https://github.com/eupyetro0224234/Generic-Clicker-Game.git
```

Entre na pasta

```bash
cd Generic-Clicker-Game
```

Instale as dependências

```bash
pip install -r github_assets/requirements.txt
```
*ou, caso prefira instalar manualmente

```bash
pip install pillow pycryptodome pygame requests pytz
```

Rode o projeto

```bash
python app.py
```

---

## Contribuições

Contribuições são muito bem-vindas! Siga esses passos:

1. Faça um fork do projeto  

2. Crie uma branch com sua feature:  
```bash
git checkout -b minha-feature
```

3. Faça commits das suas alterações:
```bash
git commit -m 'Minha nova feature'
```

4. Dê push na branch:
```bash
git push origin minha-feature
```

5. Abra um Pull Request

## Envie suas sugestões e contribuições

Se você quiser contribuir com alguma parte do código ou tiver sugestões para melhorar o projeto, por favor, preencha este formulário:

[Formulário de Contribuição e Sugestões](https://forms.gle/fh1ZR7tAoz226bpT8)

Sua participação é muito importante para o crescimento e melhoria contínua do projeto!

## Licença Customizada

Você tem permissão para usar e modificar este projeto livremente.
No entanto, a publicação de quaisquer versões modificadas ou derivadas do projeto só pode ser feita com fork do projeto ou mediante minha autorização prévia e expressa.
Ou seja, alterações são permitidas para uso pessoal ou interno, mas para distribuir ou publicar essas modificações, você pode fazer um fork ou deve obter minha permissão.

## Mods

Atualmente, esse projeto suporta apenas modificações diretas no código e modificação via código simplificado no background. Eu sei que isso não é nada prático, mas estou trabalhando junto com as atualizações em um jeito menos complexo de criar mods.

## Questões Comuns

- Esse jogo foi feito com Inteligencia Artificial?

**Sim, os códigos foram revisados e muitos bugs foram corrigidos com auxílio de ia.**

- Por que meu antivírus apita ou bloqueia meu programa mesmo ele sendo seguro?

**Antivírus usam técnicas para identificar comportamentos ou códigos suspeitos, mesmo em programas legítimos. Isso pode causar falsos positivos, quando o antivírus sinaliza algo como vírus sem que haja ameaça real. Isso acontece porque o software pode conter padrões ou operações parecidas com malware, ou por ser um arquivo novo e desconhecido.**

- Quando será lançada a versão 1.0?

**Essa é uma pergunta que eu nem eu sei responder. Só lançarei a versão final quando esse jogo tiver cumprido minhas expectativas.**

- Você pretende ir lançando atualizações frequentes?

**Como uma pessoa só trabalhando, as versões iniciais serão lançadas ao poucos. Então sim, o jogo não acabará na 1.0. Mesmo assim, ferramentas de modding serão disponíveis para a comunidade trabalhar e melhorar o meu jogo**

- Somente o Windows receberá o jogo ou outros sistemas também?

**Por ser complicado ir portando o código conforme eu vou o modificando, por um bom tempo somente o windows terá suporte. Após o lançamento da 1.0 e de ter um sistema agradável pra mods, eu pensarei na portabilidade. Usando o [GameHub](https://gamehubemulator.com/), é possível jogar, mas é extremamente lento. Lançarei uma atualização para melhorar o desempenho em algum momento.**

- Preciso do Python instalado?

**Baixando o setup ou a pasta das releases, não. Mas caso você clome o repositório e queira o executar no seu pc, sim.**

- Os dados salvos de uma versão funcionam em outra?

**Infelizmente não funcionam muito bem. Pois o arquivo de save é atualizado a cada segundo, seja por novas adições ou por organização. Em algum momento, não terá mais modificações no arquivo de save, assim, estabilizará.**

## Contato
Pyetro — contato.eupyetro022@gmail.com

## Créditos
* [Minecraft Wiki](https://pt.minecraft.wiki/w/Livro_Encantado): Gif do Livro Encantado
* [Stardew Valley Wiki](https://pt.stardewvalleywiki.com/Controles_m%C3%B3veis): Ícone de configurações
* [Potion Permit Wiki](https://potion-permit.fandom.com/pt-br/wiki/Di%C3%A1rio_M%C3%A9dico): Botão do menu de upgrades
* [Bloons Wiki](https://bloons.fandom.com/wiki/List_of_Bloons): Corações do mini evento
* [Modpack Crash Landing](https://www.curseforge.com/minecraft/modpacks/crash-landing): Som de conquista concluída
* [Kindergarten Wiki](https://kindergarten.fandom.com/wiki/Nugget): Trabalhador
* [Doors OST](https://www.youtube.com/watch?v=GUPtSENNsdg): Áudio do Mini Evento
* Minecraft 1.7.10 Forge: Botão de concluído para iniciar o jogo com mods
* Dragon Mania: Botão de fechar os menus

## Changelogs
<details> <summary> 0.0.06 - 04/01/26 </summary>

Como prometido, um bom tempo sem atualizações. Essa atualização ficou pronta a tipo, uma ou duas semanas atrás. Só esperei mais um pouco e adicionei umas coisas que viriam na 0.0.06.1 (ou 07) pois hoje fazem 6 meses desde que começei o projeto e lancei a primeira release. Além disso, é a primeira release de 2026. Feliz ano novo!



- Cronometro de tempo de jogo,
- Reset via R removido, agora somente via console ou apagando o arquivo de save,
- No console, agora pode se usar reset achievements points invés de usar um de cada vez,
- Textos dos upgrades corrigidos,
- Agora, no menu de configurações, é possível controlar o volume dos 2 áudios atuais do jogo, além disso, é possível diminuir o brilho de fundo pra até -35%,
- Conquista nova: Tudo em um,
- Agora não da mais que o app não responde ao carregar o jogo,
- Estatísticas agora são visíveis,
- Sequência,
- Upgrades novos e ajuste nos preços e nomes,
- Quando há algum problema com save, invés de mostrar uma mensagem que no fim ia começar o save do 0, já deixei pra começar direto (por isso, não mexa nos arquivos de save),
- Data para desbloqueio das conquistas;
- Os upgrades agora sobem de preço quando comprados,
- Reformulação visual da tela de escolher os mods (isso foi adiantado pra próxima versão),
- Textos no console resumidos/retirados,
- Agora é possível ganhar pontos enquanto o jogo está fechado,
- Botão de fechar menus do Dragon Mania,
- Bug que ao abrir o menu de configurações com os controles sendo exibidos, ele o fechava corrigido,
- Efeito "glassmorphism" para as opções do menu, pros upgrades, pros controles e para o aviso de conquista concluida.

</details>

<details>  <summary> 0.0.05.2 - 25/10/25 </summary>

Quem diria eu que na minha cabeça ia sumir vindo aqui fazer patches pra coisas mínimas que passaram desapercebidas sksk

- Mini eventos estavam muitos ops, pois eu tinha aumentado usado para testes,
- O upgrade de segurar pra ganhar pontos agora funciona só no botão de subir pontos,
- Nos menus de configurações e eventos, não aparece mais o menu de sair ao dar alt f4.

</details>

 <details> <summary>0.0.05.1 - 24/10/25</summary>

Essa aqui demorou, mas foi por um bom motivo. DEZENAS de bugs que eu só consegui ajustar lendo calmamente cada parte do código estão resolvidos e com algumas mudanças. Além disso, eu só manti como 0.0.05.1 pois agora, para mim, uma atualização de verdade tem que ter pelo menos 5 adições. Não conta remover 1 texto, por exemplo, tem que ser coisas decentes de verdade. Decidi também fazer uma atualização que geralmente serve pra correção de bugs ser uma grande atualização.

- A partir de agora, os assets utilizados pelo jogo não precisam mais ser baixados via internet, eles já vem junto com o executável;
- Jogo agora em tela cheia;
- Ajuste nas posições e tamanhos dos elementos em geral;
- Alguns opções inúteis removidas do menu de configurações;
- Novo design pro menu de conquistas;
- Dezenas de micro adições/mudanças que se eu mencionasse aqui, essa lista estaria maior do que está;
- Agora há um limite de 10 trabalhadores, além de um nerf, pois estavam muito roubados;
- Novos comandos e ajustes pro console;
- Alguns atalhos como U para listar os upgrades e M para abrir as opções do menu;
- Novo upgrade: Trabalhador - Mini Eventos. Ele apenas faz com que se o trabalhador passar pelo mini evento, ele é clicado;
- Áudio para o mini evento: Da ost de Doors;
- Mais um tipo de mini evento.

Foi isso, espero que tenham gostado. Tchau! Eu estou sem saber o que adicionar, então, por mais um tempo, não terão atualizações a n~ão ser que sejam pra mellhorar o desempenho. Até breve.

</details>

<details>
  <summary>0.0.05 - 01/08/25</summary>

Mais uma atualização minúscula pra coleção.

- Nova conquista: Tríplice Coroa,
- Botões para sair dos menus que usam a tela toda sem precisar apertar o esc,
- Ao clicar encima do aviso de atualização disponível, o link das releases é aberto no seu navegador,
- Opção de ativar texturas removida,
- Agora o trabalhador fica embaixo dos elementos, evitando não poder clicar na posição que ele está,
- Eventos adicionados,
- Imagens poderão ser exibidas no código agora.
</details>

<details>
  <summary>0.0.04 - 18/07/25</summary>

Essa é uma grande atualização (provavelmente não a maior em adições pro jogo, mas a maior em mecanicas e personalização)

- Nome alterado para **Generic Clicker Game** (ou abreviado para GCM),
- Primeiro suporte para mods adicionado: Mudar o fundo,
- Confirmação de reset ao apertar o R,
- Agora a quantidade de clicks dados no mini evento são salvos,
- Tela para escolher o mod que queira usar, caso tenha mais de um,
- Correção do bug nas conquistas dos mini eventos (antes ao reiniciar o jogo, ele resetava a quantidade de mini eventos clicados),
- Novo upgrade: Segurar com o botão esquerdo sobe 2 pontos por segundo,
- Novas conquistas: Antes da automação, vem a fase manual e Perfeição 1.5
- Novas configuraçãos: Pular loading e Menu vertical,
- Sistema de carregar dados de uma versão para a outra (funcionando somente a partir dessa),
- Clicar em qualquer lugar da tela com o menu de upgrades aberto o fecha agora,
- Otimização de código: Como o jogo não abre o terminal, todos os prints() sem importância foram removidos,
- Trabalhador temporário, que te da até 5000 pontos.

</details>

<details>
  <summary>0.0.03.1 - 11/07/25</summary>

Igualmente a 0.0.02.1, essa atualização serviu apenas para correções.

- Bug ao clicar em qualquer lugar da tela enquanto o evento está ativo considera como click no evento corrigido,
- Bug do ícone não exibir na barra de tarefas corrigido (a partir da segunda vez que abrir o jogo, o ícone aparecerá normalmente).

</details>

<details>
  <summary>0.0.03 - 11/07/25</summary>

Essa foi uma pequena atualização, o foco dela foi correção de bugs.
  
- Novas conquistas,
- Aviso sonoro de conquistas concluídas,
- Alterações visuais no menu de configurações e controles,
- Mini evento adicionado,
- Ícone novo,
- Novos comandos para o console,
- Configurações novas: Manter o console aberto e Mostrar conquistas ocultas,
- Correção de diversos bugs,
- O precisa apertar enter para abrir agora.

</details>

<details>
  <summary>0.0.02.1 - 07/07/25</summary>
  
- Aviso de update disponível adicionado.

Funcionando apenas dessa versão pra mais recentes. Pras anteriores, infelizmente não funciona.

</details>

<details>
  <summary>0.0.02 - 07/07/25</summary>
  
Ajustes e otimizações de código, reduzindo por volta de 4mb do tamanho do arquivo.

- Sistema para baixar arquivos novo,
- Menu de upgrades,
- Comandos e console,
- Novo menu para conquistas,
- Novos menus: Conquistas e Sair,
- Fade Off ao clicar para sair,
- Confirmação de saída.

</details>

<details>
  <summary>0.0.01 - 04/07/25</summary>
  
Lançamento inicial.

</details>
