# Projeto Frame Flow

## Visão Geral

O **Frame Flow** é um sistema distribuído de processamento de vídeos baseado em microsserviços. Cada serviço é responsável por uma parte do domínio e os serviços se comunicam via APIs HTTP e eventos distribuídos utilizando Redis Pub/Sub. Os principais serviços do sistema são:

- **Auth Service**: Gerencia cadastro de usuários, autenticação e validação de tokens JWT.
- **Upload Service**: Recebe vídeos enviados pelos usuários, valida o tamanho (limite de 100 MB) e extensão (por exemplo, `.mp4`, `.mkv`, `.avi`, `.mov`), realiza o upload para AWS S3, armazena metadados no banco de dados e publica o evento `FILE_UPLOADED` no Redis.
- **Process Service**: Baixa os vídeos do S3, processa-os com FFmpeg para extrair frames em intervalos de 10 segundos, comprime os frames em um arquivo ZIP e faz o upload desse ZIP para o S3; por fim, publica o evento `FILE_PROCESSED`.
- **Download Service**: Realiza o streaming (download) dos arquivos ZIP processados do S3 para os usuários.
- **Orchestrator**: Implementa o padrão Saga para coordenar o fluxo distribuído. Ele escuta os eventos do Redis Pub/Sub e, com base no tipo de evento, despacha as ações adequadas (usando o padrão Strategy e validação com Pydantic).

Além desses serviços, o ambiente conta com:
- **PostgreSQL**: Cada serviço utiliza seu próprio banco de dados ou esquema para garantir a separação dos dados.
- **Redis**: Utilizado para operações rápidas de cache e, principalmente, para Pub/Sub centralizado.
- **AWS S3**: Armazenamento dos vídeos, frames extraídos e arquivos ZIP.

## Arquitetura e Decisões (DDD e Event Storming)

### Conceitos de DDD e Bounded Contexts
Cada serviço foi desenvolvido como um contexto delimitado (bounded context):

- **Auth Context**: Responsável pelo gerenciamento de usuários e autenticação.
- **Upload Context**: Responsável pelo recebimento de vídeos e publicação de eventos.
- **Process Context**: Responsável pelo processamento de vídeos (extração de frames, compressão em ZIP).
- **Download Context**: Responsável pelo download/streaming dos arquivos processados.
- **Saga Orchestrator**: Coordena o fluxo de eventos e integra os serviços usando o padrão Saga.

### Event Storming
Os principais eventos mapeados no sistema são:
- `FILE_UPLOADED`: Gerado pelo Upload Service após o envio do vídeo.
- `PROCESS_FILE`: Disparado pelo Orchestrator para iniciar o processamento.
- `FILE_PROCESSED`: Gerado pelo Process Service após o processamento e compressão.
- (Outros eventos, como `FILE_FAILED`, podem ser adicionados conforme necessário.)

Cada evento é validado utilizando modelos Pydantic, garantindo a integridade dos dados.

### Decisões Arquiteturais
- **Microserviços Independentes**: Cada serviço é implementado com FastAPI de forma assíncrona, permitindo escalabilidade horizontal e melhor utilização de recursos.
- **Comunicação via Redis Pub/Sub**: O Redis foi escolhido por sua performance e pela capacidade de gerenciar comunicação em tempo real entre serviços, centralizando o fluxo de eventos.
- **Limites Otimizados**:  
  - **Tamanho do Arquivo**: Limite de 100 MB para uploads, definido para balancear desempenho e experiência do usuário.
  - **Extração de Frames**: A extração em intervalos de 10 segundos foi definida com base em testes de performance e para garantir qualidade e eficiência no processamento.
- **Persistência de Dados**: Cada serviço possui seu próprio banco (ou esquema) no PostgreSQL, garantindo a separação dos dados.

```pgsql
                          +--------------------+
                          |    Auth Service    |
                          | (Cadastro/Login)   |
                          +---------+----------+
                                    |
                                    v
                          +--------------------+
                          |   Upload Service   | <-- Recebe arquivo de vídeo, envia para S3 e publica FILE_UPLOADED
                          +---------+----------+
                                    |
                                    v
                          +--------------------+
                          |   Process Service  | <-- Processa vídeo (FFmpeg), extrai frames, comprime em ZIP, envia para S3, publica FILE_PROCESSED
                          +---------+----------+
                                    |
                                    v
                          +--------------------+
                          |  Download Service  | <-- Permite download/streaming do ZIP processado
                          +---------+----------+
                                    ^
                                    |
                          +--------------------+
                          | Orchestrator       | <-- Coordena eventos entre serviços via Redis Pub/Sub
                          +--------------------+
                                    ^
                                    |
                              +-----------+
                              |   Redis   |
                              |  Pub/Sub  |
                              +-----------+
                                    ^
                                    |
                              +--------------+
                              | PostgreSQL   |
                              | (Múltiplos DBs) |
                              +--------------+
                                    ^
                                    |
                              +--------------+
                              |   AWS S3     |
                              | (Armazenamento)|
                              +--------------+

```