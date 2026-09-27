## **Proposta de Projeto**

## **Nome da Aplicação: Termômetro do Crédito ou Radar Econômico**

## Ideia de painel que traduz indicadores do **Bacen** em uma leitura simples para pessoas físicas e pequenos empresários decidirem sobre crédito, dívida e investimento. Servindo como ferramenta de auxílio na tomada de decisão

Esse tipo de ferramenta é muito comum em empresas de grande porte como grandes bancos, fintechs e investidoras.

## **Tecnologias e relação com os requisitos do projeto:**

| **Requisito**               | **Como resolver**                                                                                                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework web               | **Streamlit** (Python)                                                                                                                                                        |
| ---                         | ---                                                                                                                                                                           |
| Banco de dados              | **SQLite** (ou PostgreSQL na nuvem) para cachear os dados baixados da API e guardar preferências do usuário                                                                   |
| ---                         | ---                                                                                                                                                                           |
| Script web (JavaScript)     | Componente customizado no Streamlit, ex: um gráfico interativo em JS puro (Chart.js) ou um pequeno widget de tooltip/animação                                                 |
| ---                         | ---                                                                                                                                                                           |
| Nuvem                       | Por questões de custo e segurança, faremos o deploy no **Streamlit Community Cloud** (grátis) ou Render/Railway; banco pode ficar no **Supabase** (Postgres usando free tier) |
| ---                         | ---                                                                                                                                                                           |
| Uso de API                  | **API SGS do Bacen**, ela tem os dados necessários para construirmos os indicadores do projeto. (<https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados>)              |
| ---                         | ---                                                                                                                                                                           |
| Acessibilidade              | Contraste de cores no padrão WCAG AA (para tornar o site/aplicativo inclusivo para pessoas com deficiência).                                                                  |
| ---                         | ---                                                                                                                                                                           |
| Testes                      | Testes automatizados para garantir que o tratamento dos dados e a **busca de informações na API** funcionem corretamente, mesmo sem conexão real durante os testes.           |
| ---                         | ---                                                                                                                                                                           |
| Controle de versão          | **Git + GitHub**, com branches e commits organizados (mostrar no relatório).                                                                                                  |
| ---                         | ---                                                                                                                                                                           |
| Análise de dados (opcional) | Cálculo de variação percentual, médias móveis, correlação simples entre juros e inadimplência                                                                                 |
| ---                         | ---                                                                                                                                                                           |

## **Escopo funcional (iniciaremos com uma lista bem definida de indicadores)**

Deixar os principais indicadores configurados:

1. **Seleção de indicadores** (multiselect na sidebar):
   - Taxa Selic (código SGS 432)
   - IPCA (433)
   - Inadimplência das operações de crédito PF/PJ (21082 / 21083)
   - Saldo de crédito / endividamento das famílias (29034 ou similar)
   - Taxa de desemprego (24369, via PNAD contínua)
2. **Filtros**: período (data início/fim), granularidade (mensal), comparação entre 2 indicadores no mesmo gráfico (eixo duplo)

3. **Visualizações**: gráficos de linha (algo que integre bem com Streamlit) + um card com "leitura simples" (ex: "Selic subiu 0,5 p.p. no último trimestre → tendência de juros mais altos no crédito")

4. **Painel de alerta simples**: um "semáforo" (verde/amarelo/vermelho) calculado a partir de regras simples (ex: se inadimplência subir X% e Selic subir, sinaliza "cautela ao contrair dívida"), aqui entra a análise de dados de forma leve, sem IA pesada

5. **Cache local em SQLite**: evita bater na API toda hora pra evitar timeout, guarda histórico consultado (talvez aqui fazer uma pré-carga do histórico)

6. **Exportar** dados filtrados em CSV caso o usuário deseje utilizar fora da plataforma (por exemplo em excel para cruzar com informações externas).

## **Proposta de utilidade pública**

**Problema:**

Pessoas físicas e pequenos empresários tomam decisões de crédito (financiar, parcelar, pegar empréstimo, renegociar dívida) sem entender o contexto macroeconômico (poucos olham esse indicador), não sabem ler taxa Selic, IPCA ou índice de inadimplência, e esses dados do Bacen, embora públicos, são apresentados de forma técnica e pouco acessível ao cidadão comum.

Embora os dados sejam públicos e acessíveis a todos, é comum vermos essas informações sendo utilizadas apenas em grandes bancos e fintechs.

**Solução:**

Um **painel gratuito** e simples que traduz esses indicadores em uma "leitura de cenário mais simples e de fácil interpretação" (ex: "juros em alta, inadimplência subindo, não é um bom momento para novos empréstimos") e mostra tendências visuais, ajudando:

- **Pessoas físicas**: a decidir o melhor momento para financiar um bem, quitar dívidas ou negociar juros
- **Pequenos empresários/MEIs**: a planejar capital de giro, decidir se é hora de buscar crédito para o negócio ou esperar cenário melhor, entender risco de inadimplência de clientes no setor
- **Educação financeira**: democratiza o acesso a dados que hoje só analistas econômicos costumam interpretar

Como possibilidade mostrar a tendência dos indicadores para um melhor mapeamento da situação.

Isso **conecta a utilização de tecnologias diretamente com a política pública de educação financeira** e reforça a relevância social do projeto.

**Repositório do Projeto Integrador 2:**

Link para o desenvolvimento do projeto

<https://github.com/levelmax-dev/pi_2_termometro_do_credito>

**Cenário/comunidade externa escolhida**

O projeto será desenvolvido de forma remota, com validação junto a uma comunidade externa formada por pessoas físicas e pequenos empreendedores/MEIs da região de São José dos Campos (SP) e adjacências, público diretamente afetado pelo cenário de recorde de inadimplência no Brasil.

A interação com essa comunidade ocorrerá por meio de conversas informais (inicialmente), e apresentação de protótipos a corretores (que trabalham com empréstimos), buscando entender como essas pessoas hoje tomam decisões de crédito e quais dificuldades encontram para interpretar indicadores econômicos.

**Plano de Ação preliminar (rascunho, sujeito a atualização)**

- Será desenvolvido no template fornecido.

**Algumas Tarefas da Lista**

1. Criar repositório no GitHub e estrutura inicial do projeto
2. Levantar e validar os códigos de séries do SGS/Bacen a serem usados (Selic, IPCA, inadimplência, endividamento)
3. Modelar banco de dados (schema SQLite) para cache dos dados da API
4. Desenvolver módulo de consumo da API SGS (ETL) com tratamento de erros
5. Escrever testes automatizados (pytest) para funções de tratamento de dados e chamadas de API
6. Construir interface inicial em Streamlit (seleção de indicadores e filtros de período)
7. Implementar gráficos interativos com comparação entre indicadores
8. Desenvolver componente customizado em JavaScript (ex: widget ou visualização complementar)
9. Aplicar critérios de acessibilidade
10. Realizar deploy em ambiente de nuvem (Streamlit Community Cloud / Render)
11. Ajustes finais, documentação e preparação da entrega