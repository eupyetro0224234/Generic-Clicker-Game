# Just Another Generic Clicker Game, But With References

![Badge de versão](https://img.shields.io/badge/version-0.0.02.1-alpha-blue) ![Licença Proprietária Customizada](https://img.shields.io/badge/license-Proprietária%20Customizada-blue)

**Desative o tradutor do seu navegador ao ler**

> _Just Another Generic Clicker Game, But With References é um projeto que nasceu com a minha curiosidade e para o meu aprendizado. Como grande fâ de jogos como Stardew Valley e Minecraft, quis criar um jogo de clicker para ir evoluindo com o tempo._

---

## Sumário

- [Sobre](#sobre)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Contribuições](#contribuições)
- [Mods e Texturas](#mods-e-texturas)
- [Questões Comuns](#questões-comuns)
- [Envie suas sugestões e contribuições](#envie-suas-sugestões-e-contribuições)
- [Licença Customizada](#licença-customizada)
- [Contato](#contato)
- [Créditos](#créditos)
- [Changelogs](#changelogs)
---

## Sobre

Este projeto é um jogo clicker desenvolvido em Python utilizando a biblioteca Pygame. Inspirado por jogos clássicos do gênero, ele oferece uma experiência divertida e simples de acumular pontos clicando em um botão central.
O jogo inclui funcionalidades como sistema de upgrades para melhorar o ganho de pontos, conquistas para motivar o jogador a alcançar metas, menus interativos para configurar controles e visualizar o progresso, além de efeitos visuais que tornam a jogabilidade mais envolvente.
Desenvolvido como um projeto pessoal, o objetivo é aprender e aplicar conceitos de programação de jogos, interfaces gráficas, persistência de dados e experiência do usuário. O código é modular e comentado, facilitando futuras melhorias e adaptações.

---

## Funcionalidades

✅**Clique para ganhar pontos**
- O jogador clica no botão central para acumular pontos.

✅**Sistema de upgrades**
- Com os pontos acumulados, o jogador pode comprar upgrades que aumentam a quantidade de pontos por clique, como "Auto Clique", "Pontos em dobro" e "Mega clique".

✅**Sistema de conquistas**
- Conquistas são desbloqueadas automaticamente conforme o jogador atinge determinados marcos, e podem ser visualizadas em um menu específico.

✅**Menus interativos**
- Menus de Configurações, Controles, Conquistas e Upgrades, acessíveis por ícones no canto da tela, com animações de abertura e fechamento.

✅**Efeitos visuais de clique**
- Pequenas animações aparecem ao clicar, mostrando "+1" para dar feedback visual ao jogador.

✅**Sistema de salvamento automático**
- Pontuação, conquistas desbloqueadas, upgrades adquiridos e configurações são salvos automaticamente para que o progresso seja mantido entre sessões.

✅**Tela de carregamento animada**
- Apresenta mensagens e uma barra de progresso enquanto o jogo carrega, melhorando a experiência do usuário.

✅**Controle por teclado**
- Permite usar atalhos como ESC para fechar menus e R para resetar a pontuação e conquistas.

✅**Interface responsiva e estilizada**
- Usa imagens externas para ícones e botões, animações suaves, e disposição intuitiva dos elementos na tela.

---

## Instalação

Siga os passos abaixo para rodar o projeto localmente (caso prefira, vá em [releases](https://github.com/eupyetro0224234/just-another-generic-clicker-game-but-with-references/releases) e baixe o executável mais recente):

<span style="font-size:22px; color:red;"><b><i>Certifique-se de ter pelo menos o Python 3.11 instalado (recomendo o 3.11.9) e a versão mais recente do Git</i></b></span>


Clone o repositório
```bash
git clone https://github.com/eupyetro0224234/just-another-generic-clicker-game-but-with-references.git
```

Entre na pasta

```bash
cd just-another-generic-clicker-game-but-with-references
```

Instale as dependências

```bash
pip install -r requirements.txt
```
*ou, caso prefira instalar manualmente

```bash
pip install certifi==2025.6.15 charset-normalizer==3.4.2 idna==3.10 pillow==11.3.0 pygame==2.6.1 requests==2.32.4 urllib3==2.5.0
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
No entanto, a publicação de quaisquer versões modificadas ou derivadas do projeto só pode ser feita mediante minha autorização prévia e expressa.
Ou seja, alterações são permitidas para uso pessoal ou interno, mas para distribuir ou publicar essas modificações, você deve obter minha permissão.

## Mods e Texturas

Atualmente, esse projeto suporta apenas modificações diretas no código. Eu sei que isso não é nada prático, mas estou trabalhando em um jeito menos complexo de criar e carregar mods.

## Questões Comuns

- Por que meu antivírus apita ou bloqueia meu programa mesmo ele sendo seguro?

**Antivírus usam técnicas para identificar comportamentos ou códigos suspeitos, mesmo em programas legítimos. Isso pode causar falsos positivos, quando o antivírus sinaliza algo como vírus sem que haja ameaça real. Isso acontece porque o software pode conter padrões ou operações parecidas com malware, ou por ser um arquivo novo e desconhecido.**


- Quando será lançada a versão 1.0?

**Essa é uma pergunta que eu nem eu sei responder. Só lançarei a versão final quando esse jogo tiver cumprindo minhas expectativas.**

- Você pretende ir lançando atualizações frequentes?

**Como uma pessoa só trabalhando, as versões iniciais serão lançadas ao poucos. Então sim, o jogo não acabará na 1.0. Mesmo assim, ferramentas de modding serão disponíveis para a comunidade trabalhar e melhorar o meu jogo**

- Somente o Windows receberá o jogo ou outros sistemas também?

**Por ser complicado ir portando o código conforme eu vou o modificando, por um bom tempo somente o windows terá suporte. Após o lançamento da 1.0 e de ter um sistema agradável pra mods, eu pensarei na portabilidade.**

- Preciso do Python instalado?

**Baixando o .exe das releases, não. Mas caso você clome o repositório e queira o executar no seu pc, sim.**

- Os dados salvos de uma versão funcionam em outra?

**Atualmente, não, pois o arquivo que gerencia os dados salvos sofre mudanças constantes, assim, dificultando muito que mantenha a mesma estrutura pra todas as versões**

## Contato
Pyetro — eu.pyetro.022@gmail.com

## Créditos
* Minecraft Wiki: [Gif do Livro Encantado](https://pt.minecraft.wiki/w/Livro_Encantado)
* Stardew Valley Wiki: [Ícone de configurações](https://pt.stardewvalleywiki.com/Controles_m%C3%B3veis)
* Potion Permit Wiki: [Botão do menu de upgrades](https://potion-permit.fandom.com/pt-br/wiki/Di%C3%A1rio_M%C3%A9dico)
* Bloons Wiki: [Mini corações que dão pontos](https://bloons.fandom.com/wiki/List_of_Bloons)

## Changelogs

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
