#import timeit
print("\n###Services###\n")

#controller.js onde estão as chamadas dos Rests
arqCtrl = open('..\\configuracaoSistemaCtrl.js', 'r')

#todas as factory/services.js do módulo 'app.services'
arqService = open('..\\allServices.js', 'r')

#route funcionalidade / domínio
#

##Variaveis
conteudoCtrl = []
listaServicesUsing = []

#variavel lista com todo o ctrl.js para extração das chamadas de rests.
#limpando alguns caracteres especiais para facilidar no IN
conteudoCtrl = arqCtrl.read()\
                    .replace('\n', '').replace('\t', '')\
                    .replace('(', ',').replace(')', ',')\
                    .replace('{', '').replace('}', '')\
                    .replace(';', ',').replace(' ', '')\
                    .split(',')

for n, item in enumerate(conteudoCtrl):
    if "Service." in item:
        serviceTemp = item.strip()
        
        if not "alertService." in serviceTemp:
            listaServicesUsing.append(serviceTemp)

#Ordenando para facilitar debbug
#TODO Quando possuir mais de 1 REST da mesma base (EndpointBase), 
# fazer outro For para pegar todos as RESTS do EndpointBase para não precisar ler/buscar 
# desde a linha 1 novamente no IN (if callService[0] in conteudoService:) = performance
listaServicesUsing.sort()

#tranformando em lista para localizar o name service final correto em casos nomes iguais (ex: getById)
listaConteudoService = arqService.readlines()

#func para pegar a Operação do restful http.
def getVerboHttp():
    verbo = 'GET'

    if "post" in temp:
        verbo = "POST"
    elif "put" in temp:
        verbo = "PUT"
    elif "delete" in temp:
        verbo = "DELETE"
    elif "patch" in temp:
        verbo = "PATCH"

    return verbo

#estrutura 'fake' do Services.js por meio da lista, cada item corresponde a uma linha.
#TODO fazer uma estrutura independente de tamanho da estrutura da callService/service.js, 
# atual só funciona para estrutura com 3 nós (if len(callService) == 3:)
for n, item in enumerate(listaServicesUsing):

    #quebrando a chamada do service pelo ctrl.js para assimilar com a estrutura em lista do Services.js
    callService = item.split('.')
    
    achouFactory = False #= cada factory/service.js do módulo 'app.services'
    achouBaseServ = False
    achouService = False

    if "fileManagerService" in callService[0]:
        continue

    #print(n+1, ' - ', item)
    #suportando apenas 3 nós, TODO
    if len(callService) == 3:
        for n2, conteudoService in enumerate(listaConteudoService):
            if callService[0] in conteudoService:
                achouFactory = True
                continue
            elif not achouFactory:
                continue
            
            if achouFactory and callService[1] in conteudoService:
                achouBaseServ = True
                continue
            elif not achouBaseServ:
                continue

            if achouBaseServ and callService[2] in conteudoService or achouService:
                achouService = True
                temp = conteudoService.strip().replace('"', "'").replace(' ', '')

                verbo = getVerboHttp()

                if "'" in temp:
                    indexIni = temp.find("'")
                    indexFin = temp.find("'", indexIni + 1)

                    endpoint = temp[indexIni : indexFin]

                    index1Plus = temp.find("+")
                    
                    if index1Plus > -1 and "+" in temp[index1Plus + 1:]:
                        temp = temp[index1Plus + 1:]
                        index2Plus = temp.find("+")
                        temp = temp[index2Plus:]
                        
                        if "," in temp and temp.find(")") > temp.find(",") or temp.find(")") == -1:
                            indexFimParam = temp.find(",") 
                        else:
                            indexFimParam = temp.find(")")

                        temp = temp[:indexFimParam]

                        temp = temp.split("/")

                        for n, tmp in enumerate(temp):
                            if "+" in tmp:
                                tmp = tmp.replace("+'", "}")
                                tmp = tmp.replace("'+", "{")
                                tmp = tmp.replace("+", "{")
                            else:
                                tmp = tmp.replace("'", "")
                                endpoint += "{0}".format(tmp)       
                                continue
                            
                            if (n + 1) == len(temp):
                                iTmp = tmp[:-1].find("{")
                                tmp += "}" if tmp[iTmp:].find("}") == -1 else tmp

                                endpoint += "{0}".format(tmp)                               
                            else:
                                endpoint += "{0}/".format(tmp)

                    endpoint = endpoint.lower() + "'"
                    print(verbo, endpoint)
                    break
                else:
                    continue