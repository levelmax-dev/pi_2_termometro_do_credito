<<<<<<< HEAD
# 🌡️ Termômetro do Crédito

**Termômetro do Crédito: aplicação para apoio à compreensão do cenário econômico por pequenos empreendedores**

Projeto Integrador em Computação II — UNIVESP
Bacharelado em Ciência de Dados, Tecnologia da Informação e Engenharia da Computação
Polo Jacareí / São José dos Campos — Tutor: Aurélio de Souza Oliveira

**Integrantes:** Adriano Neves de Oliveira · Diogo Jaderson Ferreira Santos ·
Francislene Oliveira Gomes · Luís Alberto Costa da Conceição ·
Marcos Patrick da Costa Cerbino · Pedro Henrique Alencar Barbosa ·
Ramon Galana Luglio · Rudnei Augusto de Paula Santos

Aplicação web que traduz indicadores técnicos do Banco Central (Selic,
IPCA, inadimplência, endividamento das famílias e desemprego) em uma
leitura simples e visual, para apoiar pequenos empreendedores na
compreensão do cenário econômico e na tomada de decisões sobre crédito,
dívida e investimento.

## Status atual do projeto

- ✅ MVP (Produto Mínimo Viável) funcional e navegável
- ✅ 25 testes automatizados implementados, todos passando
- ✅ Conversa inicial de descoberta realizada com um pequeno
  empreendedor da região de São José dos Campos (etapa "ouvir")
- ⏳ Validação da solução junto à comunidade externa (pendente)
- ⏳ Deploy em ambiente de nuvem (pendente — hoje a aplicação roda
  apenas localmente)

## Funcionalidades

- **Seleção de indicadores** (multiselect) e **filtro de período**
- **Comparação de 2 indicadores** no mesmo gráfico com **eixo duplo**
- **Médias móveis de 3 e 6 meses** sobre cada indicador, para leitura
  de tendências
- **Cartões de "leitura simples"** (ex.: "Selic subiu 0,5 p.p. no
  último trimestre → tendência de juros mais altos no crédito")
- **Painel de alerta ("semáforo")**: verde / amarelo / vermelho,
  calculado por regras simples e transparentes, renderizado com um
  **componente customizado em JavaScript puro (Chart.js)**
- **Cache local em SQLite**, evitando chamadas repetidas à API e com
  **fallback automático** para o cache se a API estiver indisponível
- **Exportação dos dados filtrados em CSV**
- **Acessibilidade**: critérios da WCAG 2.2, contraste adequado,
  foco visível por teclado, rótulos `aria-label` no gauge e nos
  controles
- **Testes automatizados** (pytest) para API, banco de dados,
  indicadores e regras do semáforo — todos com *mocks*, sem depender
  de conexão real durante os testes

## Estrutura do projeto

```
termometro_credito/
├── app.py                     # Aplicação Streamlit (interface principal)
├── api_client.py               # Consumo da API SGS/Bacen (ETL + retries + fallback)
├── database.py                 # Cache SQLite + preferências do usuário
├── indicators.py               # Catálogo de indicadores + médias móveis + variações
├── alerts.py                   # Regras do semáforo de alerta
├── utils.py                    # Formatação, CSV, helpers de acessibilidade
├── components/
│   └── semaforo_widget.py      # Componente JS customizado (Chart.js) do gauge
├── tests/                      # Testes automatizados (pytest)
│   ├── test_api_client.py
│   ├── test_database.py
│   ├── test_indicators.py
│   └── test_alerts.py
├── .streamlit/config.toml      # Tema (cores com contraste WCAG AA)
├── requirements.txt
└── data/                       # Criado automaticamente (banco SQLite local)
```

## Banco de dados

O cache local usa SQLite com três tabelas (ver `database.py`):

| Tabela | Finalidade | Chave |
|---|---|---|
| `indicador_cache` | Armazena os valores de cada série baixada da API (um valor por indicador/data) | `codigo` + `data` (composta) |
| `log_sincronizacao` | Registra cada tentativa de atualização junto à API do Bacen (sucesso ou falha) | `id` (autoincremento) |
| `preferencias_usuario` | Guarda preferências do usuário, como os últimos indicadores selecionados | `chave` |

Não há chave estrangeira imposta pelo SQLite entre `log_sincronizacao`
e `indicador_cache`, mas as duas se relacionam logicamente pelo campo
`codigo`: cada indicador pode ter várias tentativas de sincronização
registradas. O diagrama desse esquema está no Relatório Parcial
(seção 2.4, "Criar e prototipar").

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

A aplicação abre em `http://localhost:8501`. Na primeira execução, os
dados são baixados da API do Bacen e armazenados em
`data/termometro_credito.db`; nas próximas, o cache é usado
automaticamente (renovado a cada 24h ou ao clicar em "Atualizar dados
agora").

> Requer Python 3.10 ou superior (o código usa sintaxe como `str | None`).

## Como rodar os testes

```bash
pytest tests/ -v
```

Os testes usam a biblioteca `responses` para simular as respostas da
API do Bacen (sem necessidade de internet) e um banco SQLite temporário
isolado por teste (`tmp_path` do pytest), garantindo que não afetam o
banco real da aplicação.

## Deploy em nuvem (próxima etapa)

Opção recomendada (gratuita): **Streamlit Community Cloud**.

1. Suba este projeto para o repositório GitHub do grupo.
2. Em [share.streamlit.io](https://share.streamlit.io), conecte o
   repositório e aponte para `app.py`.
3. O deploy detecta automaticamente o `requirements.txt`.

Alternativas: Render ou Railway (usando o mesmo `requirements.txt` e
um *start command* `streamlit run app.py --server.port $PORT
--server.address 0.0.0.0`).

## Indicadores utilizados (API SGS/Bacen)

| Indicador | Código SGS |
|---|---|
| Taxa Selic | 432 |
| IPCA | 433 |
| Inadimplência — Pessoa Física | 21082 |
| Inadimplência — Pessoa Jurídica | 21083 |
| Endividamento das famílias | 29034 |
| Taxa de desemprego (PNAD Contínua) | 24369 |

## Aviso

Este painel tem finalidade educativa e não constitui recomendação
financeira, de investimento ou de crédito.
=======
# pi_2_termometro_do_credito
Ideia de painel que traduz indicadores do Bacen em uma leitura simples para pessoas físicas e pequenos empresários decidirem sobre crédito, dívida e investimento.
>>>>>>> 1a4f6b1a48f6495d8df299e90894a8568b4947bb
