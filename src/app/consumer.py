import json
import os

from dotenv import load_dotenv
from pyflink.common import SimpleStringSchema, Types, WatermarkStrategy
from pyflink.common.serialization import Encoder
from pyflink.datastream import MapFunction
from pyflink.datastream.connectors import FileSink
from pyflink.datastream.connectors.kafka import (KafkaOffsetsInitializer,
                                                 KafkaSource)
from pyflink.datastream.stream_execution_environment import \
    StreamExecutionEnvironment


class JsonParser(MapFunction):
    """
    Classe para realizar o parse de objetos JSON.

    Esta classe implementa a interface `MapFunction` e contém um método `map` 
    que recebe uma string JSON como entrada e retorna o objeto JSON correspondente.

    Métodos
    -------
    map(value)
        Recebe uma string JSON e retorna o objeto Python correspondente.
    
    Parâmetros
    ----------
    value : str
        String em formato JSON que será convertida em objeto Python.
    
    Retorna
    -------
    dict
        Objeto JSON convertido a partir da string de entrada.
    """
    def map(self, value) -> dict:
        return json.loads(value)
    
class AccessValues(MapFunction):
    """
    Classe para acessar valores específicos de um dicionário JSON.

    Esta classe implementa a interface `MapFunction` e contém um método `map` 
    que extrai valores de um dicionário JSON com as chaves 'nome', 'email', 
    'empresa' e 'cargo', retornando-os em uma string formatada.

    Métodos
    -------
    map(json_dict)
        Recebe um dicionário JSON e retorna uma string formatada com os valores 
        associados às chaves específicas.
    
    Parâmetros
    ----------
    json_dict : dict
        Dicionário JSON contendo as chaves 'nome', 'email', 'empresa' e 'cargo'.
    """
    def map(self, json_dict) -> str:
        nome = json_dict.get('nome')
        email = json_dict.get('email')
        empresa = json_dict.get('empresa')
        cargo = json_dict.get('cargo')
        return str(f"Nome: {nome}, Email: {email}. Empresa: {empresa}, Cargo: {cargo}")

class SourceStream(object):
    """
    Classe para configurar e gerenciar o fluxo de dados de uma fonte Kafka e enviar os dados processados para um destino.

    A classe `SourceStream` inicializa o ambiente de execução de fluxo e configura a leitura de dados de um tópico Kafka,
    com a opção de armazenar os dados processados em um arquivo de saída.

    Métodos
    -------
    __init__()
        Inicializa o ambiente de execução do Flink, adiciona o conector Kafka e define o paralelismo.
    
    create_kafka_source_stream(bs_server: str, topic: str, consumer_group: str)
        Cria uma fonte de dados Kafka, configurando o servidor, o tópico e o grupo de consumidores, e define a partir
        de onde o consumo do tópico deve iniciar.
    
    create_sink_stream(output_path: str)
        Processa o fluxo de dados da fonte Kafka usando as classes `JsonParser` e `AccessValues`, e envia o resultado
        para um arquivo de destino.
    
    Parâmetros
    ----------
    bs_server : str
        Endereço do servidor de bootstrap Kafka.
    topic : str
        Tópico Kafka do qual os dados serão lidos.
    consumer_group : str
        Identificador do grupo de consumidores do Kafka.
    output_path : str
        Caminho do arquivo onde os dados processados serão salvos.
    """
    def __init__(self, path_jar:str):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars(f"file:///{path_jar}")
        self.env.set_parallelism(1)

    def create_kafka_source_stream(self, bs_server:str, topic:str, consumer_group:str) -> None:
        kafka_source = KafkaSource.builder() \
            .set_bootstrap_servers(bs_server) \
            .set_topics(topic) \
            .set_group_id(consumer_group) \
            .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
            .set_value_only_deserializer(SimpleStringSchema()) \
            .build()
        
        self.data_stream = self.env.from_source(kafka_source, WatermarkStrategy.no_watermarks(), "Kafka Source")
    
    def create_sink_stream(self, output_path:str) -> None:
        parsed_stream = self.data_stream.map(JsonParser(), output_type=Types.MAP(Types.STRING(), Types.STRING()))
        sink = FileSink.for_row_format(output_path, Encoder.simple_string_encoder("utf-8")).build()
        parsed_stream.map(AccessValues(), output_type=Types.STRING()).sink_to(sink)
        self.env.execute('Stream Processing Pipeline')

if __name__ == '__main__':
    # Carregar arquivo .env
    load_dotenv()

    # Variáveis de ambiente
    PATH_JAR = os.getenv(r'PATH_JAR')
    BS_SERVER = os.getenv('BS_SERVER')
    OUTPUT_FILES_PATH = os.getenv('OUTPUT_FILE_PATH')
    TOPIC = os.getenv('TOPIC')
    CONSUMER_GROUP = os.getenv('CONSUMER_GROUP')

    # Stream Consumer
    datastream = SourceStream(PATH_JAR)
    datastream.create_kafka_source_stream(BS_SERVER, TOPIC, CONSUMER_GROUP)
    datastream.create_sink_stream(OUTPUT_FILES_PATH)