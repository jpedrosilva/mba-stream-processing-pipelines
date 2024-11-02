# Observação
Caso ocorra algum tipo de erro na leitura das variáveis de ambiente (arquivo .env), fechar e reabrir o terminal para que o ambiente virtual seja reinicializado corretamente.

# Descrição do Projeto
 
Este projeto realiza a leitura de arquivos JSON e os envia para um sistema de processamento em tempo real utilizando Kafka e PyFlink. O objetivo é capturar e processar dados em tempo real de maneira organizada.
 
## Funcionalidades
 
- Mapeamento de arquivos JSON de entrada na pasta `src/app/data/in`.
- Envio dos arquivos mapeados para um tópico do Kafka.
- Leitura dos dados em tempo real com PyFlink e escrita dos dados processados em arquivos de saída na pasta `src/app/data/out`.
- Os arquivos de saída são organizados em pastas no formato `YYYY-MM-DD--HH`, facilitando a organização e recuperação dos dados.
 
## Como Executar o Projeto (Windows)?

1. Instalar o pyenv-win via PowerShell:
`Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"` 
2. Na pasta do projeto (root) executar o comando: `pyenv local 3.11.7`
3. Instale o [Poetry](https://python-poetry.org/) para gerenciamento de dependências: `pip install poetry`
4.  Instale as dependências do projeto:
	   `poetry install --only main` 
5.  Configure o caminho do arquivo `.jar` necessário para o PyFlink:
   -   Localize o arquivo `.jar` na pasta `src/app/jar`.
   -   Edite a variável `PATH_JAR` no arquivo `.env` para apontar para o caminho completo do arquivo `.jar`.
6.  Inicie os containers do Docker (necessário para rodar o Kafka e outros serviços): `docker-compose up -d`
7.  Em terminais separados, execute os seguintes comandos para iniciar o consumidor e o produtor (em sua respectiva ordem):
   `poetry run python src/app/consumer.py`
   `poetry run python src/app/producer.py`

 
Agora, o sistema está configurado para capturar os dados JSON de entrada, processá-los em tempo real e salvar os resultados na estrutura de saída especificada.
 
## Tecnologias Utilizadas
 
-   Kafka
-   PyFlink
-   Poetry
-   Python
-   Docker