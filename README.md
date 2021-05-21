# tsp_pcv_vrotas

Nota para mim: https://gist.github.com/stephenhardy/5470814 (Steps to clear out the history of a git/github repository)
-para remover nome da empresa do código.

Este programa oferece uma interface para a fácil resolução da otimização de trajetos, a partir do Problema do Caixeiro Viajante (Travelling Salesman Problem). Dados os endereços inicial e final, e um conjunto de endereços intermediários, o programa retorna a ordem ótima, curta e de baixa duração entre os endereços passados. Útil para economizar tempo e distância percorrida na locomoção urbana e otimizar custos de operações que utilizam deslocamento automotivo.

O usuário deve rodar o osrm_backend em sua máquina para que o programa possa encontrar as distâncias ou durações mais curtas.
Pré-requisitos:
Python 3+
Docker
OSRM
Mapa local

Como baixar no Windows:

1. Instale o Python no computador acessando https://www.python.org/downloads/ (Na instalação, marque "adicionar Python ao PATH")

2. Instale o programa Docker em https://www.docker.com/products/docker-desktop (Na instalação, marque "adicionar Docker ao PATH")

3. Abra o Prompt de Comandos e digite: docker pull osrm/osrm-backend:latest

4. Aguarde até terminar.

5. Baixe o mapa local através de https://www.geofabrik.de/data/download.html , escolhendo o território onde deseja efetuar as rotas.
   -> Por exemplo: https://download.geofabrik.de/south-america/brazil/centro-oeste-latest.osm.pbf

6. Verifique o local do seu computador para onde você baixou o mapa, copie o endereço da localização.

7. Com o Docker aberto, aperte com o botão direito sobre seu ícone e clique em Settings.

8. Em Settings acesse Resources, depois File Sharing, e insira o endereço que você copiou referente ao local dos dados de mapa baixados.

9. Vá no Prompt de Comandos novamente e digite: docker run -t -v local_dos_dados:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/arquivo_de_dados.osm.pbf
   -> Por exemplo: docker run -t -v C:/Users/Victor/Documents/Python/osrm/data:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/centro-oeste-latest.osm.pbf
   -> Note que as barras devem ser / e não \

10. Em seguida digite no Prompt de Comandos: docker run -t -v local_dos_dados:/data osrm/osrm-backend osrm-contract /data/arquivo_de_dados.osm.pbf
   -> Por exemplo: docker run -t -v C:/Users/Victor/Documents/Python/osrm/data:/data osrm/osrm-backend osrm-contract /data/centro-oeste-latest.osm.pbf

11. Aguarde (Isso deve demorar um pouco)

12. Para terminar as configurações, digite no Prompt de Comandos: docker run -t -i -p 5000:5000 -v local_dos_dados:/data osrm/osrm-backend osrm-routed /data/arquivo_de_dados.osm
   -> Por exemplo: docker run -t -i -p 5000:5000 -v C:/Users/Victor/Documents/Python/osrm/data:/data osrm/osrm-backend osrm-routed /data/centro-oeste-latest.osm

13. Agora o OSRM estará disponível no Docker. para ativá-lo, abra o Dashboard do Docker, coloque o mouse em cima do OSRM e aperte no botão Run / Start.

14. Por fim, execute o arquivo Python aqui presente e utilize a ferramenta à vontade!

Em caso de dúvidas: victor_costa_caldas@hotmail.com
Tentarei responder o quanto antes.
