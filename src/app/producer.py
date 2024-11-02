import json
import os
import time

from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError


def on_send_success(record_metadata) -> None:
    """
    Função de callback para confirmação de envio bem-sucedido de uma mensagem.

    Esta função é chamada quando uma mensagem é enviada com sucesso para um tópico Kafka, 
    exibindo informações sobre o tópico, a partição e o offset da mensagem enviada.
    """
    print("topic", record_metadata.topic, 
          "partition", record_metadata.partition, 
          "offset", record_metadata.offset)

def on_send_error(exception) -> None:
    """
    Função de callback para tratar falhas no envio de uma mensagem.

    Esta função é chamada quando ocorre uma falha ao tentar enviar uma mensagem para um tópico Kafka, 
    exibindo a exceção que causou o erro.
    """
    print("Falha no envio da mensagem:", exception)

def create_producer(bs_server: str) -> KafkaProducer:
    """
    Cria e configura um produtor Kafka para enviar mensagens.

    Esta função inicializa um produtor Kafka, configurando o servidor de bootstrap e 
    o serializador de valores para enviar mensagens em formato JSON.

    Parâmetros
    ----------
    bs_server : str
        Endereço do servidor de bootstrap Kafka, utilizado para estabelecer a conexão.
    """
    producer = KafkaProducer(bootstrap_servers=[bs_server], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    return producer

def producer_send_message(producer: KafkaProducer, message: dict, topic: str) -> str:
    """
    Envia uma mensagem ao Kafka utilizando um produtor especificado.

    Esta função tenta enviar uma lista de mensagens em formato JSON para um tópico Kafka. 
    Se o envio for bem-sucedido, a função `on_send_success` é chamada como callback. 
    Em caso de erro, a função `on_send_error` é acionada. A função trata exceções de envio e 
    realiza um `flush` para garantir que todas as mensagens pendentes sejam enviadas antes de finalizar.

    Parâmetros
    ----------
    producer : KafkaProducer
        Instância do produtor Kafka utilizada para enviar as mensagens.
    message : dict
        Dicionários a serem enviados como mensagens JSON.
    topic : str
        Nome do tópico Kafka para o qual as mensagens serão enviadas.
    """
    try:
        producer.send(topic=topic, value=message).add_callback(on_send_success).add_errback(on_send_error)
    except KafkaError as e:
        print(f"Erro na execução da função 'producer_send_message': {e}")
        pass
    producer.flush()
    time.sleep(2)

def get_all_input_files(path: str) -> list[str]:
    """
    Obtém uma lista de todos os arquivos em um diretório especificado.

    Esta função lista todos os arquivos presentes no caminho fornecido, ignorando subdiretórios.

    Parâmetros
    ----------
    path : str
        Caminho do diretório onde os arquivos serão listados.

    Retorna
    -------
    list
        Lista contendo os nomes de todos os arquivos no diretório especificado.
    """
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files

if __name__ == '__main__':
    # Carregar arquivo .env
    load_dotenv()

    # Variáveis de ambiente
    BS_SERVER = os.getenv('BS_SERVER')
    INPUT_FILES_PATH = os.getenv('INPUT_FILE_PATH')
    TOPIC = os.getenv('TOPIC')

    # Stream Producer
    for file in get_all_input_files(INPUT_FILES_PATH):
        producer = create_producer(BS_SERVER)
        with open(os.path.join(INPUT_FILES_PATH, file), 'r') as f:
            data = json.load(f)
            for element in data:
                producer_send_message(producer=producer, message=element, topic=TOPIC)