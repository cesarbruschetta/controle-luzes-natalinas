# Automação das luzes de Natal

O projeto consulta diariamente o nascer e o pôr do sol e usa a Tuya Cloud para controlar a tomada, sem exigir que o computador esteja na mesma rede local. A estrutura separa `clients` (APIs externas), `services` (regras da aplicação) e `utils` (rotinas de suporte).

## Requisitos

- Python 3.13.15, selecionado pelo asdf em `.tool-versions`
- Poetry 2.x
- Um projeto Tuya Cloud configurado com acesso ao dispositivo

Instale as dependências:

```bash
cd /caminho/para/controle-luzes-natalinas
asdf install
poetry install
```

O arquivo `.env` usa atribuições simples (`NATAL_...=...`). Para carregá-lo no Bash e exportar as variáveis para o processo do Poetry, execute:

```bash
set -a
source .env
set +a
```

`NATAL_TUYA_API_KEY` e `NATAL_TUYA_API_SECRET` são o Access ID/Client ID e Access Secret/Client Secret do projeto Tuya. A região deve coincidir com a região configurada no painel. O código de função costuma ser `switch_1`, mas pode variar conforme o dispositivo. O projeto Tuya precisa ter as APIs necessárias autorizadas e a conta do app vinculada ao projeto.

Pydantic Settings lê as variáveis do ambiente do processo; a aplicação não carrega `.env` sozinha. O `set -a` faz com que as atribuições do `source` sejam exportadas para o Poetry. As coordenadas e o fuso têm valores padrão neste projeto. O fuso padrão atual é `UTC`; para horário civil de São Paulo, use `America/Sao_Paulo`.

O `.env` está ignorado pelo Git. Restrinja as permissões do arquivo para que só o usuário do projeto possa lê-lo (`chmod 600 .env`). Evite colocar segredos diretamente em comandos `export`, pois eles podem ficar salvos no histórico do shell.

## Execução

Execute uma vez para instalar ou atualizar as tarefas do cron. Isso também migra as entradas antigas para o ambiente virtual criado pelo Poetry:

```bash
poetry run natal-agendar
```

O agendador consulta a API diariamente às 01:00, liga no pôr do sol e desliga no nascer do sol. As outras tarefas do crontab são preservadas. O daemon do cron precisa suportar `CRON_TZ` para aplicar o fuso configurado.

Como o cron não herda automaticamente as variáveis exportadas no terminal, o bloco gerenciado grava nelas os valores usados no agendamento, inclusive as credenciais Tuya. O crontab pertence ao usuário e normalmente só pode ser lido por ele; leve isso em conta ao escolher a conta do sistema que executará o cron. Execute `poetry run natal-agendar` novamente após alterar qualquer variável para atualizar o bloco.

Teste o controle manualmente:

```bash
poetry run natal-tomada --action on
poetry run natal-tomada --action off
```

Os horários solares são arredondados para o próximo minuto, porque cron não agenda segundos. O computador precisa estar ligado e conectado à internet no horário.

## Estrutura

```text
src/luzes_natalino/
├── clients/    # Sunrise/Sunset e Tuya Cloud
├── services/   # Agendamento e controle das luzes
├── utils/      # Funções de cron
├── cli_control.py
├── cli_schedule.py
└── settings.py
tests/
```