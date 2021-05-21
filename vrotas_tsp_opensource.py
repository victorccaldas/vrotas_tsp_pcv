from tkinter.scrolledtext import ScrolledText
from geopy.geocoders import Nominatim
from datetime import timedelta
from datetime import datetime
from tkinter import *
import webbrowser
import googlemaps
import requests
import polyline
import folium
import sys

    
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

geolocator = Nominatim(user_agent="enderecos_routing")

google_key = ''

cor_dos_labels = 'white'

def aplicarRotas():
    global lista_enderecos
    global obs_google

    lista_enderecos = end_clientes.get(1.0, END).split("\n")
    #lista_enderecos.remove

    while '' in lista_enderecos:
        lista_enderecos.remove('')

    try:
        canvas.delete(vermapa1_button)
    except:
        pass
    try:
        canvas.delete(vermapa2_button)
    except:
        pass
    try:    
        canvas.delete(obs_google)
    except:
        pass
    
    if servico_escolhido.get() == "Google":
        servicoRotas_label.config(bg='#d4d0cf', text=servico_escolhido.get())
        obs_google = canvas.create_window(460, 440, window=Label(root_ends_routing, bg='#d4d0cf',text="Obs: o Google otimiza\n no máximo 23 endereços\ne desenha no máx.\n10 caminhos", font=('helvetica', 8)))
        
        try:
            G_routing()
        except:
            print("Deu errado")
            canvas.delete(distance_notoptimal_label)
            canvas.delete(duration_notoptimal_label)
            canvas.delete(distance_optimal_label)
            canvas.delete(duration_optimal_label)

            #erro_label.delete('1.0',END)
            #erro_label.insert(END,sys.exc_info())
            #erro_label.configure(bg='#bf8e88')

    elif servico_escolhido.get() == "OSRM":
        try: canvas.delete(obs_google)
        except: pass
        servicoRotas_label.config(bg='#d4d0cf', text=servico_escolhido.get())
        otimização = OSRM_routing('otimizar',lista_enderecos, endereco_inicio.get(), endereco_fim.get())
        if type(otimização) == list:
            resultado_otimizado.config(bg='#d39994') # light red
            resultado_otimizado.delete(1.0,END)
            resultado_otimizado.insert(END,'Endereços inválidos:\n\n'+'\n'.join(otimização))
            return
            
        duracao = otimização['duration']/60
        distancia = otimização['distance']/1000
        enderecos_otimizados = [lista_enderecos[int(x)] for x in otimização['best_order']]

        não_otimização = OSRM_routing('nao_otimizar',lista_enderecos, endereco_inicio.get(), endereco_fim.get())
        duracao_ñotima = não_otimização['duration']/60
        distancia_ñotima = não_otimização['distance']/1000

        distance_optimal_label = canvas.create_window(600, 430, window=Label(root_ends_routing, bg='#d3e6d3', text=("Distância: "+str("%.1f" % distancia)+" km"), anchor="w", font=('helvetica', 10)))
        duration_optimal_label = canvas.create_window(600, 455, window=Label(root_ends_routing, bg='#d3e6d3', text=("Duração: "+str("%.1f" % duracao)+" min"), anchor="w", font=('helvetica', 10)))

        distance_notoptimal_label = canvas.create_window(90, 430, window=Label(root_ends_routing, bg='#e8d8b7', text=("Distância: "+str("%.1f" % distancia_ñotima)+" km"), anchor='w', font=('helvetica', 10)))
        duration_notoptimal_label = canvas.create_window(90, 455, window=Label(root_ends_routing, bg='#e8d8b7', text=("Duração: "+str(("%.1f" % duracao_ñotima)+" min")), anchor='w', font=('helvetica', 10)))


        # inserir outro text box com enderecos_otimizados
        resultado_otimizado.delete(1.0,END)
        resultado_otimizado.insert(END,'\n'.join(enderecos_otimizados))
        resultado_otimizado.config(bg='white')

        # Botões de ver as rotas (mapa1.html e mapa2.html)
        vermapa1_button = canvas.create_window(260, 440, window=Button(text="Ver rota antes", width=15,command=lambda:verRotaNoMapa('mapa1'), bg='#579482', fg='white', font=('helvetica', 13, 'bold')))
        vermapa2_button = canvas.create_window(770, 440, window=Button(text="Ver rota depois", width=15,command=lambda:verRotaNoMapa('mapa2'), bg='#579482', fg='white', font=('helvetica', 13, 'bold')))

 
def Waze_routing():
    start_address = endereco_inicio.get()
    end_address = endereco_fim.get()
    region = 'SA'
    route = WazeRouteCalculator.WazeRouteCalculator(start_address, end_address, region)
    route.calc_route_info()

def get_map_folium(melhor_rota, coords_clientes, nome_mapa):
    # criando mapa
    mapa = folium.Map(location=[(melhor_rota['start_point'][0] + melhor_rota['end_point'][0])/2, 
                             (melhor_rota['start_point'][1] + melhor_rota['end_point'][1])/2], 
                   zoom_start=12)
    
    # traçando caminho
    #print(melhor_rota['polyline'])
    folium.PolyLine(melhor_rota['route'], weight=8, color='blue', opacity=0.5).add_to(mapa)

    # plotando inicio e fim
    folium.Marker(location=melhor_rota['start_point'], tooltip="Início", icon=folium.Icon(icon='play', color='green')).add_to(mapa)
    folium.Marker(location=melhor_rota['end_point'],tooltip="Final", icon=folium.Icon(icon='stop', color='red')).add_to(mapa)
    
    # plotando clientes
    contagem = 0
    for coordenada in coords_clientes:
        contagem +=1
        lat = coordenada.split(',')[0]
        lng = coordenada.split(',')[1]
        folium.Marker(location=(lat, lng), popup="Este é o "+str(contagem)+"º waypoint", tooltip=contagem).add_to(mapa)
    mapa.save(nome_mapa+".html")

def osrm_obter_trajeto_nao_otimo(lista_waypoints, coordenada_inicio, coordenada_final):
    # invertendo ordem das coordenadas inicio e fim
    coord_inicial_lng_lat = (coordenada_inicio.split(",")[1]+','+coordenada_inicio.split(",")[0]).replace(' ','')
    coord_final_lng_lat = (coordenada_final.split(",")[1]+','+coordenada_final.split(",")[0]).replace(' ','') 
    
    wps_lng_lat = [(i.split(',')[1]+","+i.split(',')[0]).replace(" ","") for i in lista_waypoints]

    # transformando waypoints em uma string unica , e adicionando coord inicial e final
    wp_string = coord_inicial_lng_lat+';'
    for i in wps_lng_lat:
        wp_string += i+';'
    wp_string += coord_final_lng_lat

    # Resultados ROUTE
    route_url = 'http://localhost:5000/route/v1/driving/{}?steps=true&annotations=true&continue_straight=false'.format(wp_string)
    print(route_url)
    route_results = requests.get(url=route_url)
    route_data = route_results.json()
    polylines_list = polyline.decode(route_data['routes'][0]['geometry'])

    # organizando resultados
    rota = {'polyline':route_data['routes'][0]['geometry'],
                    'route': polylines_list,
                    'legs':route_data['routes'][0]['legs'], 
                    'start_point': [route_data['waypoints'][0]['location'][1], route_data['waypoints'][0]['location'][0]],
                    'end_point': [route_data['waypoints'][-1]['location'][1], route_data['waypoints'][-1]['location'][0]],
                    'duration':route_data['routes'][0]['duration'],
                    'distance':route_data['routes'][0]['distance']}
    
    get_map_folium(rota, lista_waypoints, 'mapa1')

    return rota

def osrm_obter_trajeto(lista_waypoints,coordenada_inicio, coordenada_final):
    # invertendo ordem das coordenadas inicio e fim
    coord_inicial_lng_lat = (coordenada_inicio.split(",")[1]+','+coordenada_inicio.split(",")[0]).replace(' ','')
    coord_final_lng_lat = (coordenada_final.split(",")[1]+','+coordenada_final.split(",")[0]).replace(' ','') 
    
    # eliminando duplicatas e invertendo ordem dos waypoints
    #waypoints_sem_duplicatadas = list(dict.fromkeys(lista_waypoints))
    #wps_lng_lat = [(i.split(',')[1]+","+i.split(',')[0]).replace(" ","") for i in waypoints_sem_duplicatadas]
    wps_lng_lat = [(i.split(',')[1]+","+i.split(',')[0]).replace(" ","") for i in lista_waypoints]

    # transformando waypoints em uma string unica , e adicionando coord inicial e final
    wp_string = coord_inicial_lng_lat+';'
    for i in wps_lng_lat:
        wp_string += i+';'
    wp_string += coord_final_lng_lat
    # Resultados TRIP
    trip_url = 'http://localhost:5000/trip/v1/driving/{}?roundtrip=false&source=first&destination=last&steps=true&annotations=true&geometries=polyline&overview=simplified'.format(wp_string)
    #print(trip_url)
    trip_results = requests.get(url=trip_url)
    trip_data = trip_results.json()
    polylines_list = polyline.decode(trip_data['trips'][0]['geometry'])
    #print(trip_data['waypoints'])
    #waypoints_optimal_order = [(i['waypoint_index'], i['location']) for i in trip_data['waypoints']]
    
    # Esta optimal order é diferente da do Google: pro exemplo [5,2,3,1,0,4]
    # No Google, seria 0- 5º end passado, 1- 2º end passado, 2- 3º end passado, 3- 1º end passado, 4- 0º end passado, 5- 4º end passado
    # No OSRM, deve ser: 5- 0º end passado, 2- 1º end passado, 3- 2º end passado, 1- 3º end passado, 0- 4º end passado, 4- 5º end passado
        # E depois colocado em ordem: 0- 4º end passado, 1- 3º end passado, 2- 1º end passado, 3- 2º end passado, 4- 5º end passado, 5- 0º end passado
        # então a ordem ótima em relação aos ends passados na vdd é: [4,3,1,2,5,0]
    # Portanto preciso ordenar a lista_waypoints na ordem certa.

    # nessa lista, os endereços foram passados em ordem do primeiro ao ultimo. Os numeros representam a ordem que
    # devem ser visitados no formato otimizado
    recommended_order = [i['waypoint_index']-1 for i in trip_data['waypoints'][1:-1]]
    lista_reordenando = [(x,recommended_order.index(x)) for x in recommended_order]
    lista_reordenando.sort()
    waypoints_optimal_order = [x[1] for x in lista_reordenando]

    # organizando resultados
    melhor_rota = {'polyline':trip_data['trips'][0]['geometry'],
                    'route': polylines_list,
                    'legs':trip_data['trips'][0]['legs'], 
                    'start_point': [trip_data['waypoints'][0]['location'][1], trip_data['waypoints'][0]['location'][0]],
                    'end_point': [trip_data['waypoints'][-1]['location'][1], trip_data['waypoints'][-1]['location'][0]],
                    'best_order': waypoints_optimal_order,
                    'duration':trip_data['trips'][0]['duration'],
                    'distance':trip_data['trips'][0]['distance']}
    
    coords_otimizadas = [lista_waypoints[int(x)] for x in melhor_rota['best_order']]
    get_map_folium(melhor_rota, coords_otimizadas, 'mapa2')

    return melhor_rota

def achar_coordenada(endereco):
    import time
    global resultado
    global achar_coordenada_servico_utilizado

    if str(endereco) == 'nan' or str(endereco) == '':
        return 'Não encontrada'

    # 1) Primeiro tentar nominatim
    def meu_geolocator(client, endereco):
        return client.geocode(endereco)
        
    retrys = 0
    while True:
        try:
            resultado = meu_geolocator(geolocator,endereco)

            break
        except Exception as erro:
            print("Tentativas: "+str(retrys)+"\nErro: \n"+str(erro)+'\n')
            retrys += 1
            time.sleep(1)
            pass
        if retrys > 5:
            resultado = None
            break

    if resultado != None:
        resultado = (resultado.latitude,resultado.longitude)
        #resultado = str(geolocator.geocode(end).latitude)+','+str(geolocator.geocode(end).longitude)        
            
        achar_coordenada_servico_utilizado = "Nominatim"
        
        LAT = resultado[0]
        LNG = resultado[1]
        if -17 < LAT < -14 and -49 < LNG < -46:
            resultado = str(LAT)+","+str(LNG) #str(resultado).replace(')','').replace('(','')
            return resultado
        else:
            resultado = "Inválida: "+str(resultado)
        
    # 2) Se ñ encontrada ou fora de Brasília, tentar Google
    if type(resultado) == str or resultado == None:
        while True:
            try:
                resultado = meu_geolocator(gmaps_client,endereco)
                break
            except Exception as erro:
                print("Tentativas: "+str(retrys)+"\nErro: \n"+str(erro)+'\n')
                retrys += 1
                time.sleep(1)
                pass
            if retrys > 5:
                resultado = []
                break

        if resultado != []:
            resultado = (resultado[0]['geometry']['location']['lat'], resultado[0]['geometry']['location']['lng'])
            achar_coordenada_servico_utilizado = "Google"

            LAT = resultado[0]
            LNG = resultado[1]
            if -17 < LAT < -14 and -49 < LNG < -46:
                resultado = str(LAT)+","+str(LNG)
                return resultado
            else:
                resultado = "Inválida: "+str(resultado)

    if type(resultado) == str or resultado == [] or resultado == None:
        resultado = 'Não encontrada'
        achar_coordenada_servico_utilizado = 'nenhum'
    else:
        resultado = "Bugou em algum lugar..."   
    return resultado

def geocode_osm(endereços):
    coords_intermediarias = []
    ends_invalidos = []
    for end in endereços:
        try:
            coord_end = str(geolocator.geocode(end).latitude)+','+str(geolocator.geocode(end).longitude)        
            coords_intermediarias.append(coord_end)
        except:
            ends_invalidos.append(end)
    return coords_intermediarias, ends_invalidos

def geocode_osm_google(endereços):
    coords_intermediarias = []
    ends_invalidos = []
    for end in endereços:
        try:
            coord_end = achar_coordenada(end)
            if coord_end != 'Não encontrada':   
                coords_intermediarias.append(coord_end)
            else:
               ends_invalidos.append(end) 
        except:
            ends_invalidos.append(end)
    return coords_intermediarias, ends_invalidos

def OSRM_routing(otimizar,intermediarios, inicio, fim):
    coord_inicial = str(geolocator.geocode(inicio).latitude)+','+str(geolocator.geocode(inicio).longitude)
    coord_final = str(geolocator.geocode(fim).latitude)+','+str(geolocator.geocode(fim).longitude)
    
    if google_key == '':
        coords_intermediarias, ends_invalidos = geocode_osm(intermediarios)
    else:
        coords_intermediarias, ends_invalidos = geocode_osm_google(intermediarios)

    if len(ends_invalidos) > 0:
        print("Endereços inválidos:\n")
        [print(end) for end in ends_invalidos]
        return ends_invalidos
    else:
        if otimizar == 'otimizar':
            melhor_rota = osrm_obter_trajeto(coords_intermediarias, coord_inicial, coord_final)
            return melhor_rota
        else:
            rota = osrm_obter_trajeto_nao_otimo(coords_intermediarias, coord_inicial, coord_final)
            return rota
        

def G_routing():
    global coords_otimizado
    global nova_rota
    global distance_notoptimal_label
    global duration_notoptimal_label
    global distance_optimal_label
    global duration_optimal_label
    global enderecoslidos
    global start_address
    global vermapa1_button
    global vermapa2_button

    try:
        horario_string = horario_inicio.get()
        horario_datetime = datetime.strptime(horario_string, '%d/%m/%y %H:%M')
        
    except:
        print("A data está no formato errado.")
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,horario_string)
        enderecoerrado_label.configure(bg='#bf8e88')
        return 'stop'

    if (datetime.now() - horario_datetime).days > 0:
        print("Erro: A data está no passado.")
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,horario_string)
        enderecoerrado_label.configure(bg='#bf8e88')
        return 'stop'
    #location = gmaps_client.geocode(verificacao)
    
    lista_coords = []
    bsb_geocode = gmaps_client.geocode("Brasilia,DF")
    bsb_coords = (bsb_geocode[0]['geometry']['location']['lat'], bsb_geocode[0]['geometry']['location']['lng'])
    start_address = endereco_inicio.get()
    start_geocode = gmaps_client.geocode(start_address)
    end_address = endereco_fim.get()
    end_geocode = gmaps_client.geocode(end_address)
    
    try:
        start_coords = (start_geocode[0]['geometry']['location']['lat'],start_geocode[0]['geometry']['location']['lng'])
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,'<Debug>')
        enderecoerrado_label.configure(bg='white')
    except:
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,start_address)
        enderecoerrado_label.configure(bg='#bf8e88')
        sys.exit()
    
    try:
        end_coords = (end_geocode[0]['geometry']['location']['lat'],end_geocode[0]['geometry']['location']['lng'])
        enderecoerrado_label.configure(bg='white')
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,'<Debug>')

    except:
        enderecoerrado_label.configure(bg='#bf8e88')
        enderecoerrado_label.delete('1.0',END)
        enderecoerrado_label.insert(END,end_address)
        sys.exit()

    
    end_coords = (end_geocode[0]['geometry']['location']['lat'],end_geocode[0]['geometry']['location']['lng'])

    # criar listas de coordenadas, latitude e longitude com base nos endereços escolhidos
    enderecos_lidos = []
    try:
        for endereco in lista_enderecos:
            location = gmaps_client.geocode(endereco)
            #print(location.address)
            #print((location.latitude, location.longitude))
            lista_coords.append((location[0]['geometry']['location']['lat'], location[0]['geometry']['location']['lng']))
            enderecos_lidos.append(endereco)
    except:
        for end in lista_enderecos:
            if end in enderecos_lidos:
                pass
            else:
                print(end)
                enderecoerrado_label.configure(bg='#bf8e88')
                enderecoerrado_label.delete('1.0',END)
                enderecoerrado_label.insert(END,end)
                sys.exit()

# Rota NÃO otimizada : tempo e distância
    global directions_NaoOtimizado
    directions_NaoOtimizado = gmaps_client.directions(start_coords, end_coords, waypoints=lista_coords, departure_time=horario_datetime)
    distance_notoptimal = 0
    duration_notoptimal = 0
    legs = directions_NaoOtimizado[0]['legs']
    for leg in legs:
        distance_notoptimal = distance_notoptimal + leg['distance']['value']
        duration_notoptimal = duration_notoptimal + leg['duration']['value']

    try:
        canvas.delete(distance_notoptimal_label)
        canvas.delete(duration_notoptimal_label)
    except:
        pass

    distance_notoptimal_label = canvas.create_window(90, 430, window=Label(root_ends_routing, bg='#e8d8b7', text=("Distância: "+str("%.1f" % (distance_notoptimal/1000))+" km"), anchor='w', font=('helvetica', 10)))
    duration_notoptimal_label = canvas.create_window(90, 455, window=Label(root_ends_routing, bg='#e8d8b7', text=("Duração: "+str(("%.1f" % (duration_notoptimal/60))+" min")), anchor='w', font=('helvetica', 10)))

    directions_result = gmaps_client.directions(start_coords, end_coords, waypoints=lista_coords, optimize_waypoints = True, traffic_model = 'best_guess', departure_time=horario_datetime)

    # somando distancias e durações de cada etapa da rota
    distance = 0
    duration = 0
    legs = directions_result[0]['legs']
    
    for leg in legs:
        #distance = distance + leg.get("distance").get("value") # ambas as formas dão no mesmo
        distance = distance + legs[0]['distance']['value']
        duration = duration + legs[0]['duration']['value']

    # mostrar distância, tempo e ordem otimizada da rota
    print(str("%.1f" % (distance/1000))+" km")
    print(str(duration/60)+" min")
    print(directions_result[0]['waypoint_order'])

    # lista com endereços e coordenadas reorganizados no formato otimizado
    nova_rota = []
    coords_otimizado = []
    for wp_num in directions_result[0]['waypoint_order']:
        nova_rota.append(lista_enderecos[wp_num])
        coords_otimizado.append(lista_coords[wp_num])
    
    # transformando enderecos de lista pra string
    enderecos_otimizados = '\n'.join(nova_rota)
    #n = 0
    #while n < len(nova_rota):
    #    enderecos_otimizados = enderecos_otimizados + nova_rota[n]+"\n"
    #    n += 1

    # criar plotter, criar direções e plotar no mapa (mapa1)
    plotmap = gmplot.GoogleMapPlotter(bsb_coords[0],bsb_coords[1], 13, apikey=g_apikey)
    plotmap.directions(start_coords, end_coords, waypoints=lista_coords, optimize_waypoints = True, traffic_model = 'best_guess',departure_time=horario_datetime)
    
    # Plotando enderecos (markers) na ordem não-otimizada
    marker_label = 1
    plotmap.marker(start_coords[0],start_coords[1],precision=10, label=str(marker_label),title=str(marker_label))
    marker_label += 1
    for i in lista_coords:
        plotmap.marker(i[0],i[1],precision=10, label=str(marker_label),title=str(marker_label))
        marker_label += 1
    plotmap.marker(end_coords[0],end_coords[1],precision=10, label=str(marker_label),title=str(marker_label))

    plotmap.draw('mapa1.html')
    global duracao_otima
    global duracao_rota
    global dict_rotas

    # Plottando mapa2.html
    
    distancia_otima = 0
    duracao_otima = 0
    marker_label = 1
    anterior = start_coords
    enderecos_rotalidos = []
    dict_rotas = {}
    duracao_rota = 0
    duracao_total_da_rota = 0
    todosends = []

    plotmap = gmplot.GoogleMapPlotter(bsb_coords[0],bsb_coords[1], 13, apikey=g_apikey)
    plotmap.marker(start_coords[0],start_coords[1],precision=10, label=str(marker_label),title=start_address, color='indianred',draggable=True)
    marker_label += 1

# PENSAR EM UMA FORMA de fazer o datetime.now() calcular corretamente, visto que todos os pontos do trajeto estarão
# com departure no horário mencionado no user_input 'horario de inicio'

    for i in coords_otimizado:
        plotmap.directions(anterior, i, traffic_model ='best_guess', departure_time=horario_datetime)
        plotmap.marker(i[0],i[1],precision=10, label=str(marker_label),title=nova_rota[(marker_label-2)], color='indianred',draggable=True)
        caminho_1po1 = gmaps_client.directions(anterior, i, traffic_model ='best_guess', departure_time=horario_datetime)
        distancia_otima = distancia_otima + caminho_1po1[0]['legs'][0]['distance']['value']
        duracao_otima = duracao_otima + caminho_1po1[0]['legs'][0]['duration']['value']
        
        marker_label += 1 
        anterior = i

        duracao_rota = duracao_rota + caminho_1po1[0]['legs'][0]['duration']['value']
        enderecos_rotalidos.append(i)
        duracao_total_da_rota = (len(enderecos_rotalidos)*600) + duracao_rota # qtd de ends dos clientes lidos multiplicados por 2000 (20 min) + duracao do trajeto
        #print("total: "+str(duracao_total_da_rota))
        #print("otima: "+str(duracao_otima))
        #print("rota: "+str(duracao_rota))
        if duracao_total_da_rota > 6000: # 6000s = 100min (1h40); 50 minutos de folga do final. máx = 140min
            dict_rotas[(duracao_total_da_rota)] = enderecos_rotalidos
            #todosends = todosends + enderecos_rotalidos
            enderecos_rotalidos = []
            #enderecos_rotalidos.append(i)
            duracao_rota = 0
             

    #ctypes.windll.user32.MessageBoxW(0, dict_rotas, 'Rotas otimizadas:', 1)

    plotmap.directions(anterior, end_coords, traffic_model ='best_guess', departure_time=horario_datetime)
    plotmap.marker(end_coords[0],end_coords[1],precision=10, label=str(marker_label),title=end_address, color='indianred',draggable=True)
    # Ñ preciso incluir o tempo do ultimo endereço até o final na duracao_rota, já q não influencia no tempo pros clientes
    caminho_1po1 = gmaps_client.directions(anterior, end_coords, traffic_model ='best_guess', departure_time=horario_datetime)
    ultimoend_dur = caminho_1po1[0]['legs'][0]['duration']['value']
    distancia_otima = distancia_otima + caminho_1po1[0]['legs'][0]['distance']['value']
    duracao_otima = duracao_otima + caminho_1po1[0]['legs'][0]['duration']['value']
    #duracao_rota = duracao_rota + caminho_1po1[0]['legs'][0]['duration']['value']
    #enderecos_rotalidos.append(end_coords)
    #print("ultimo: "+str(ultimoend_dur/60))

    duracao_total_da_rota = (len(enderecos_rotalidos)*600) + duracao_rota # 1200 = 20 min
    if (duracao_total_da_rota) > 0:
        dict_rotas[(duracao_total_da_rota)] = enderecos_rotalidos
        #enderecos_clienteslidos = []
        #duracao_casaclientes = 0
        #duracao_otima = 0
    
    #print("otima: "+str(duracao_otima))
    #print("rota: "+str(duracao_rota))
    somadict = 0
    for i in dict_rotas:
        somadict = somadict +i
    
    #print("otima: "+str(duracao_otima/60))
    #print("soma dict: "+str(somadict/60))
    print("Resultado = "+str(len(coords_otimizado)*10)+" + "+str((duracao_otima/60)-(ultimoend_dur/60))+" == "+str(somadict/60))
    # (duracao_otima/60)-(ultimoend_dur/60) tem que ser igual à soma do dict - (enderecos*20)

    print(dict_rotas)

    #print("Distancia do mapa2: "+str("%.1f" % (distancia_otima/1000))+" km")
    #print("Duração do mapa2: "+str(duracao_otima/60)+" min")

    try:
        canvas.delete(distance_optimal_label)
        canvas.delete(duration_optimal_label)
    except:
        pass

    distance_optimal_label = canvas.create_window(600, 430, window=Label(root_ends_routing, bg='#d3e6d3', text=("Distância: "+str("%.1f" % (distancia_otima/1000))+" km"), anchor="w", font=('helvetica', 10)))
    duration_optimal_label = canvas.create_window(600, 455, window=Label(root_ends_routing, bg='#d3e6d3', text=("Duração: "+str("%.1f" % (duracao_otima/60))+" min"), anchor="w", font=('helvetica', 10)))

    plotmap.draw('mapa2.html') # Trajeto otimizado, porém meio bugado

    # Removendo Markers A, B do mapa:
    arquivo_mapa = open(os.path.dirname(__file__)+'/deps/mapa2.html').read()
    if 'suppress' not in arquivo_mapa:
        replaced = arquivo_mapa.replace('map: map', 'map: map, suppressMarkers: true')
        writer = open(os.path.dirname(__file__)+'\deps\mapa2.html','w')
        writer.write(replaced)
        writer.close()

    # inserir outro text box com enderecos_otimizados
    resultado_otimizado.delete(1.0,END)
    resultado_otimizado.insert(END,enderecos_otimizados)
    resultado_otimizado.config(bg='white')

    # Botões de ver as rotas (mapa1.html e mapa2.html)
    vermapa1_button = canvas.create_window(260, 440, window=Button(text="Ver rota antes", width=15,command=lambda:verRotaNoMapa('mapa1'), bg='#229399', fg='white', font=('helvetica', 13, 'bold')))
    vermapa2_button = canvas.create_window(770, 440, window=Button(text="Ver rota depois", width=15,command=lambda:verRotaNoMapa('mapa2'), bg='#229399', fg='white', font=('helvetica', 13, 'bold')))
    


def verEnderecoNoMapa(tup_lat_lng, endereço):
    plotmap = folium.Map(location=tup_lat_lng, zoom_start=12)
    folium.Marker(location=tup_lat_lng, popup="Coordenada "+str(tup_lat_lng)+"\n\n"+str(endereço), tooltip=endereço).add_to(plotmap)
    plotmap.save("map_verloc_individual_folium.html")
    webbrowser.get(chrome_path).open(os.path.dirname(__file__)+"\map_verloc_individual_folium.html")

def verRotaNoMapa(mapanum):
    webbrowser.get(chrome_path).open(os.path.dirname(__file__)+"\{}.html".format(mapanum)) 

def aplicarVerificacao(tupla_solicitada):
    global verif_result_label

    def criarEntryResultados():
        global verif_result_label
        global canvas
        verif_result_label = Entry(root_ends_routing, width=25, text=verif_result_var.get(), font=('helvetica', 9))
        canvas.create_window(355, 80, window=verif_result_label)

    try: verif_result_label.get()
    except:
        criarEntryResultados()

    if tupla_solicitada.count(1) == 0:
        checkboxes_label.config(bg='#d4d0cf', relief="solid",text="Selecione um serviço")

    elif tupla_solicitada.count(1) > 1:
        #checkboxes_label.config(bg='#d4d0cf', relief="solid",text="Marque apenas uma opção")
        checkboxes_label.config(bg='#d4d0cf', relief="solid",text="OSRM e Google")
        verificarEndereco_ambos()


    elif tupla_solicitada[0] == 1:
        checkboxes_label.config(bg='#d4d0cf', relief="solid",text="Open Street Map")
        verificarEndereco_openstreetmap()

    else:
        checkboxes_label.config(bg='#d4d0cf', relief="solid",text="Google Maps")
        verificarEndereco_google()

def verificarEndereco_ambos():
    global verificar_coords
    global vernomapa_button
    global gmaps_client

    if google_key == "":
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, 'Serviço Google indisponível. Insira uma chave de API')
        return
    verificarEndereco_openstreetmap()
    if verif_result_label.get() == 'Endereço não encontrado.':
        verificarEndereco_google()
    
def verificarEndereco_openstreetmap():
    global vernomapa_button
    global verificar_coords

    verificacao = verificar_end.get()
    try:
        canvas.delete(vernomapa_button)
    except:
        pass

    try:
        location = geolocator.geocode(verificacao)
        verificar_coords = (location.latitude, location.longitude)
        verificar_lat = location.latitude
        verificar_long = location.longitude
        verif_result_label.config(bg='#d2e8ae', width=45, relief="solid")
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, str('Local encontrado: '+str(verificar_coords)+' '))
        #verif_result_var.set(str('Endereço existe! '+str(verificar_coords)+' '))
        vernomapa_button = canvas.create_window(545, 45, window=Button(text="Ver no mapa", width=15,command=lambda:verEnderecoNoMapa(verificar_coords, verificacao), bg='#229399', fg='white', font=('helvetica', 12, 'bold')))
        
    except:
        verificar_lat = 0
        verificar_long = 0
        verif_result_label.config(bg='#c98f8b', width=25, relief="solid")
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, 'Endereço não encontrado.')
        print(sys.exc_info())

def verificarEndereco_google():
    global verificar_coords
    global vernomapa_button

    if google_key == "":
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, 'Serviço Google indisponível. Insira uma chave de API')
        return
    else:
        gmaps_client = googlemaps.Client(key=google_key)

    verificacao = verificar_end.get()
    
    try:
        canvas.delete(vernomapa_button)
    except:
        pass

    try:
        location = gmaps_client.geocode(verificacao)
        verificar_coords = (location[0]['geometry']['location']['lat'], location[0]['geometry']['location']['lng'])
        verif_result_label.config(bg='#d2e8ae', width=45, relief="solid")
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, str('Local encontrado: '+str(verificar_coords)+' '))
        vernomapa_button = canvas.create_window(555, 45, window=Button(text="Ver no mapa", width=15,command=lambda:verEnderecoNoMapa(), bg='#229399', fg='white', font=('helvetica', 12, 'bold')))
        
    except:
        verificar_lat = 0
        verificar_long = 0
        verif_result_label.config(bg='#c98f8b', width=25, relief="solid")
        verif_result_label.delete(0,END)
        verif_result_label.insert(0, 'Endereço não encontrado.')
        print(sys.exc_info())
    
def inserirApiGoogle():
    global api_label
    root_api_google = Toplevel()
    root_api_google.title('Inserir API do Google')
    canvas2 = Canvas(root_api_google, height = 150, width = 500, bg = '#bad5e8', relief = 'raised')
    canvas2.pack()

    api_atual_label = canvas2.create_window(70, 25, window=Label(root_api_google, text='API inserido:', bg = '#bad5e8', justify=LEFT, font=('helvetica', 8,'bold')))

    if google_key != '':
        api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg=cor_dos_labels, justify=LEFT, text=google_key, font=('helvetica', 8,'bold')))
    else:
        api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg=cor_dos_labels, justify=LEFT, text='Nenhuma chave encontrada.', font=('helvetica', 8,'bold')))

    key_input = Entry(root_api_google,width=70, bg='#f5f0f0')
    key_input.insert(END,google_key)
    canvas2.create_window(250, 60, window=key_input)

    def alterar():
        global link
        global api_label
        global google_key
        global servicoGoogle_ativo
        global gmaps_client

        try: canvas2.delete(api_label)
        except: pass

        try:
            # executar um teste com a key antes de atribuir à var google_key
            gmaps_client = googlemaps.Client(key=key_input.get())
            gmaps_client.geocode('Unb, Brasília, DF')
            google_key = key_input.get()
            api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg='#dcf4e4', justify=LEFT, text=google_key, font=('helvetica', 8,'bold')))
            servicoGoogle_ativo = canvas.create_window(460, 420, window=Label(root_ends_routing, bg='#dcf4e4',text='Geocode Google ativo', font=('helvetica', 9)))
            google_checkbox_var.set(1)
            google_checkbox.config(state=NORMAL)

        except googlemaps.exceptions.ApiError:
            api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg='#c98d79', justify=LEFT, text="Chave API não tem autorização para ser acessada", font=('helvetica', 8,'bold')))
        except:
            api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg='#c98d79', justify=LEFT, text="Chave API não encontrada", font=('helvetica', 8,'bold')))
    
    def desativar():
        global api_label
        global google_key
        global servicoGoogle_ativo
        google_key = ''
        
        try: canvas2.delete(api_label); canvas.delete(servicoGoogle_ativo)
        except: pass

        api_label = canvas2.create_window(250, 25, window=Label(root_api_google, bg='white', justify=LEFT, text='Nenhuma chave ativa.', font=('helvetica', 8,'bold')))
        google_checkbox_var.set(0)
        google_checkbox.config(state=DISABLED)
    alterar_api_button = Button(root_api_google,text="Alterar API", height=1, width=12,command=lambda:alterar(),wraplength=90, bg='#9ebaa7', font=('helvetica', 10, 'bold'))
    canvas2.create_window(250, 95, window=alterar_api_button)

    desativar_api_button = Button(root_api_google,text="Desativar API", height=1, width=12,command=lambda:desativar(),wraplength=90, bg='#9ebaa7', font=('helvetica', 10, 'bold'))
    canvas2.create_window(250, 130, window=desativar_api_button)

root_ends_routing = Tk()
root_ends_routing.title('vRotas - TSP / PCV Solver')
#root_ends_routing.iconbitmap('C:/Users/Victor/Desktop/market ocr/icone ricardinho.gif')



#Main window
canvas = Canvas(root_ends_routing, height = 500, width = 1000, bg = "white", relief = 'raised')
canvas.pack()

# Logo vRotas
logo_vrotas = PhotoImage(file = os.path.dirname(__file__)+"\deps\logo vRotas 9.0 mini.png")
logo_v_label = Label(root_ends_routing, image=logo_vrotas, bg='white')
logo_v_label.place(x=850, y=-5)

# Ícone
root_ends_routing.iconphoto(True, PhotoImage(file=os.path.dirname(__file__)+'\deps\icone vRotas 9.0 mini.png'))
# faiô

# checkboxes
servico_busca_selecionado = 'nenhum'
osm_checkbox_var = IntVar(value=1)
osm_checkbox = Checkbutton(root_ends_routing, text="Open Street Map", variable=osm_checkbox_var)
canvas.create_window(340, 10, window=osm_checkbox)
google_checkbox_var = IntVar(value=0)
google_checkbox = Checkbutton(root_ends_routing, text="Google", variable=google_checkbox_var, state=DISABLED)
canvas.create_window(440, 10, window=google_checkbox)
chaveapi_google = Button(root_ends_routing,text="Inserir chave API Google",width=20,command=lambda:inserirApiGoogle(), bg='#bad5e8', font=('helvetica', 9, 'bold'))
canvas.create_window(580, 10, window=chaveapi_google)

# checkbox labels
checkboxes_label_var = StringVar(root_ends_routing)
checkboxes_label_var.set('')
checkboxes_label = Label(root_ends_routing, text=checkboxes_label_var.get(), font=('helvetica', 9))
canvas.create_window(140, 70, window=checkboxes_label)

# verificar se endereço existe
verificar_label = Label(root_ends_routing, bg=cor_dos_labels, text='Checar coordenadas de endereços:', font=('helvetica', 11, 'bold'))
canvas.create_window(140, 10, window=verificar_label)

verificar_end = Entry(root_ends_routing,width=40, bg='#e8e6e6')
verificar_end.insert(END,"Escreva o endereço aqui")
canvas.create_window(140, 45, window=verificar_end)

verificarButton = Button(root_ends_routing,text="Verificar endereço",width=15,command=lambda:aplicarVerificacao((osm_checkbox_var.get(), google_checkbox_var.get())), bg='#579482', fg='white', font=('helvetica', 13, 'bold'))
canvas.create_window(355, 45, window=verificarButton)

verif_result_var = StringVar(root_ends_routing)
verif_result_var.set('')

# endereço inicial
end_inicial_label = Label(root_ends_routing, bg=cor_dos_labels,  text='Endereço inicial:', font=('helvetica', 13,'bold'))
canvas.create_window(95, 150, window=end_inicial_label)

endereco_inicio = Entry(root_ends_routing,width=25, bg='#f5f0f0')
endereco_inicio.insert(END,"UnB, Brasília, DF")
canvas.create_window(110, 180, window=endereco_inicio)

# endereço final
end_final_label = Label(root_ends_routing, bg=cor_dos_labels,  text='Endereço final:', font=('helvetica', 13,'bold'))
canvas.create_window(290, 150, window=end_final_label)

endereco_fim = Entry(root_ends_routing,width=25, bg='#f5f0f0')
endereco_fim.insert(END,"Aeroporto Internacional de Brasilia, DF")
canvas.create_window(310, 180, window=endereco_fim)

# horario de partida
#hr_partida_label = Label(root_ends_routing, bg=cor_dos_labels,  text='Data e horário de partida (00h - 23h59)', font=('helvetica', 13,'bold'))
#canvas.create_window(720, 150, window=hr_partida_label)
#horario_inicio = Entry(root_ends_routing,width=40, bg='#f5f0f0')
#horario_inicio.insert(END,str(datetime.strftime((datetime.now() + timedelta(days=1)), '%d/%m/%y %H:%M')))
#canvas.create_window(700, 180, window=horario_inicio)


# enderecos intermediarios
ends_rota_label = Label(root_ends_routing, bg=cor_dos_labels,  text='Endereços intermediários (um por linha):', font=('helvetica', 13,'bold'))
canvas.create_window(195, 215, window=ends_rota_label)


#end_clientes = ScrolledText(root_ends_routing, xscrollcommand = scrollbar.set)
end_clientes = ScrolledText(root_ends_routing,  wrap="none")
scrollbar_endclientes = Scrollbar(root_ends_routing, orient=HORIZONTAL, command=end_clientes.xview)
#end_clientes['xscrollcommand'] = scrollbar.set
end_clientes.configure(xscrollcommand=scrollbar_endclientes.set)
scrollbar_endclientes.place(x=30,y=400,width=350)
end_clientes.place(x=30, y=235, width=350, height=170)
end_clientes.insert(END,"Asa Sul, Brasília, DF\nGarvey, Brasília, DF\nSHIS Qi 23 conjunto 2 , Brasília, DF\nSHIS QL 12 conjunto 0, Brasília, DF\nSHIN qi 11 conjunto 7, Brasília, DF\nsqn 110 bloco K, Brasília, DF\nSQS 208 bloco H Asa Sul\nQNM 36 conjunto D, Taguatinga Norte\nQE 36 conjunto C, - GUARA II\nQE 15 conjunto K - GUARA II\nA.E 04 modulo B - GUARA II\nSHA conjunto 02 - ARNIQUEIRAS")

# Botão "Otimizar Rota"
canvas.create_window(460, 350, window=Label(root_ends_routing, text='→', font=('helvetica', 54))) # seta
otimizarButton = Button(root_ends_routing,text="Otimizar rota", height=2, width=12,command=lambda:aplicarRotas(), bg='#229399', fg='white', font=('helvetica', 13, 'bold'))
canvas.create_window(460, 305, window=otimizarButton)


# enderecos otimizados
canvas.create_window(670, 215, window=Label(root_ends_routing, bg=cor_dos_labels, text='Resultado / Endereços otimizados:', font=('helvetica', 13, 'bold')))
resultado_otimizado = ScrolledText(root_ends_routing, wrap="none")
scrollbar_resultado = Scrollbar(root_ends_routing, orient=HORIZONTAL, command=resultado_otimizado.xview)
resultado_otimizado.configure(xscrollcommand=scrollbar_resultado.set)
scrollbar_resultado.place(x=540,y=400,width=350)
resultado_otimizado.place(x=540, y=235, width=350, height=170)
resultado_otimizado.config(bg='#e6e6e6')

# Drop-down table
#servico_dropdown = OptionMenu(master, variable, "one", "two", "three")
servico_escolhido = StringVar(root_ends_routing)
servico_escolhido.set("OSRM")
canvas.create_window(460, 255, window=OptionMenu(root_ends_routing, servico_escolhido, "OSRM")) # ,"Google"))
servicoRotas_label = Label(root_ends_routing, bg='#d4d0cf',text=servico_escolhido.get(), font=('helvetica', 9))
canvas.create_window(460, 390, window=servicoRotas_label)


root_ends_routing.mainloop()