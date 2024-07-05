from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3

# Criação do diagrama
with Diagram("Diagrama de Rede", show=False, direction="TB"):

    # Criação do Load Balancer
    lb = ELB("Load Balancer")

    # Criação do Cluster de Web Services
    with Cluster("Web Services"):
        web1 = EC2("Web1")
        web2 = EC2("Web2")

    # Criação do Banco de Dados
    db = RDS("Database")

    # Criação do Storage
    storage = S3("Storage")

    # Definição das conexões
    lb >> [web1, web2] # Load Balancer direciona para Web1 e Web2
    web1 >> db         # Web1 conecta ao Banco de Dados
    web2 >> db         # Web2 conecta ao Banco de Dados
    db >> storage      # Banco de Dados conecta ao Storage
