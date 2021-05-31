# tsp_pcv_vrotas

Este programa oferece uma interface para a fácil resolução da otimização de trajetos, a partir do Problema do Caixeiro Viajante (Travelling Salesman Problem). Definidos os endereços inicial e final, e dado um conjunto de endereços intermediários, o programa retorna a ordem ótima (curta e de baixa duração) entre os endereços passados. Útil para economizar tempo e distância percorrida na locomoção urbana e otimizar custos de operações que fazem uso de deslocamento automotivo.

O usuário deve rodar o osrm_backend em sua máquina para que o programa possa encontrar as distâncias ou durações mais curtas.
Pré-requisitos:

Python 3+

Docker

OSRM

Mapa local

Como baixar no Windows:

1. Instale o Python no computador acessando https://www.python.org/downloads/ (Na instalação, marque "adicionar Python ao PATH")

2. Instale o programa Docker em https://www.docker.com/products/docker-desktop (Na instalação, marque "adicionar Docker ao PATH")

3. Abra o Prompt de Comandos e digite: docker pull osrm/osrm-backend:latest , aguarde até terminar.

4. Baixe o mapa do local onde deseja roteirizar trajetos através de https://www.geofabrik.de/data/download.html .
   -> Por exemplo, Centro-Oeste (Brasil): https://download.geofabrik.de/south-america/brazil/centro-oeste-latest.osm.pbf

5. Verifique o local do seu computador para onde você baixou o mapa e copie o endereço.
   -> Por exemplo: C:\Users\victor.caldas\Desktop\Projeto_Rotas\OSRM\data\centro-oeste-latest.osm.pbf
   
6. Inverta as barras do endereço: C:/Users/victor.caldas/Desktop/Projeto_Rotas/OSRM/data/centro-oeste-latest.osm.pbf

7. Vá no Prompt de Comandos novamente e digite: docker run -t -v "<local_dos_dados>:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/arquivo_de_dados.osm.pbf
   -> Por exemplo: docker run -t -v "C:/Users/victor.caldas/Desktop/Projeto_Rotas/OSRM/data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/centro-oeste-latest.osm.pbf
   -> Note que as barras devem ser / e não \

7. Em seguida digite no Prompt de Comandos: docker run -t -v "<local_dos_dados>:/data" osrm/osrm-backend osrm-partition /data/arquivo_de_dados.osrm
   -> Por exemplo: docker run -t -v "C:/Users/victor.caldas/Desktop/Projeto_Rotas/OSRM/data:/data" osrm/osrm-backend osrm-partition /data/centro-oeste-latest.osrm

8. Ao terminar, digite no Prompt de Comandos: docker run -t -v "<local_dos_dados>:/data" osrm/osrm-backend osrm-customize /data/arquivo_de_dados.osrm
   -> Por exemplo: docker run -t -v "C:/Users/victor.caldas/Desktop/Projeto_Rotas/OSRM/data:/data" osrm/osrm-backend osrm-customize /data/centro-oeste-latest.osrm

9. Por fim, digite no Prompt de Comandos: docker run -t -i -p 5000:5000 -v "<local_dos_dados>:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/arquivo_de_dados.osrm
   -> Por exemplo: docker run -t -i -p 5000:5000 -v "C:/Users/victor.caldas/Desktop/Projeto_Rotas/OSRM/data:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/centro-oeste-latest.osrm

10. Agora o OSRM estará disponível no Docker. Sempre que quiser ativá-lo ou desativá-lo: abra o Dashboard do Docker, coloque o mouse em cima do OSRM e aperte no botão Start / Stop.

11. Por fim, execute o arquivo Python aqui presente e utilize a ferramenta à vontade

Se precisar de ajuda na configuração (em inglês) acesse https://hub.docker.com/r/osrm/osrm-backend/
