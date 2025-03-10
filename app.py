import pywhatkit as kit
import csv
import os
import json
from datetime import datetime
import threading
import time
import webbrowser
from flask import Flask, render_template, request, redirect, url_for, flash
import tkinter as tk
from tkinter import ttk
import pystray
from PIL import Image, ImageTk
import sys
from plyer import notification
import logging
import pyautogui
from threading import Lock
import subprocess

def resource_path(relative_path):
    """Obtém o caminho absoluto para recursos, funciona tanto em desenvolvimento quanto com PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def get_app_paths():
    """Retorna todos os caminhos importantes do aplicativo"""
    app_data = os.path.join(os.getenv('APPDATA'), 'WhatsAppScheduler')
    
    paths = {
        'APP_DATA': app_data,
        'LOG_FILE': os.path.join(app_data, 'logs', 'envios.csv'),
        'APP_LOG': os.path.join(app_data, 'logs', 'app.log'),
        'AGENDAMENTOS_FILE': os.path.join(app_data, 'data', 'agendamentos.json'),
        'NUMEROS_FILE': os.path.join(app_data, 'data', 'numeros.json'),
        'MENSAGENS_FILE': os.path.join(app_data, 'data', 'mensagens.json')
    }
    
    # Criar estrutura de diretórios
    for path in paths.values():
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
    return paths

def setup_logging(log_file):
    """Configura o sistema de logging"""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

def initialize_files(paths):
    """Inicializa os arquivos necessários se não existirem"""
    # Template para arquivos JSON
    json_files = [paths['NUMEROS_FILE'], paths['MENSAGENS_FILE'], paths['AGENDAMENTOS_FILE']]
    for file in json_files:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    # Template para arquivo CSV de logs
    if not os.path.exists(paths['LOG_FILE']):
        with open(paths['LOG_FILE'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Responsável", "Número", "Mensagem", "Data e Hora", "Status"])

def create_app():
    """Cria e configura a aplicação Flask"""
    # Obter todos os caminhos necessários
    paths = get_app_paths()
    
    # Configurar logging
    setup_logging(paths['APP_LOG'])
    
    # Inicializar arquivos necessários
    initialize_files(paths)
    
    # Criar aplicação Flask
    app = Flask(__name__, 
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))
    
    app.secret_key = '123456'  # Em produção, use uma chave secreta mais segura
    
    # Configurar variáveis globais
    for key, value in paths.items():
        app.config[key] = value
    
    # Log de inicialização
    logging.info(f'Aplicativo iniciado em {datetime.now()}')
    
    return app

# Inicialização global
app = create_app()
server_running = True

agendamentos_lock = Lock()

# Exportar variáveis para uso em outros módulos
APP_DATA = app.config['APP_DATA']
LOG_FILE = app.config['LOG_FILE']
AGENDAMENTOS_FILE = app.config['AGENDAMENTOS_FILE']
NUMEROS_FILE = app.config['NUMEROS_FILE']
MENSAGENS_FILE = app.config['MENSAGENS_FILE']

# Carrega ou cria os arquivos de armazenamento
def carregar_dados():
    global NUMEROS_GRAVADOS, MENSAGENS_GRAVADAS, agendamentos
    
    if os.path.exists(NUMEROS_FILE):
        with open(NUMEROS_FILE, 'r', encoding='utf-8') as file:
            NUMEROS_GRAVADOS = json.load(file)
    else:
        NUMEROS_GRAVADOS = [
            {"nome": "Cliente A", "numero": "+5511999999999"},
            {"nome": "Cliente B", "numero": "+5511888888888"}
        ]
        salvar_numeros()

    if os.path.exists(MENSAGENS_FILE):
        with open(MENSAGENS_FILE, 'r', encoding='utf-8') as file:
            MENSAGENS_GRAVADAS = json.load(file)
    else:
        MENSAGENS_GRAVADAS = [
            "Olá, tudo bem?",
            "Estamos entrando em contato para avisar sobre uma reunião importante.",
            "Lembre-se de revisar os documentos enviados anteriormente."
        ]
        salvar_mensagens()

    if os.path.exists(AGENDAMENTOS_FILE):
        with open(AGENDAMENTOS_FILE, 'r', encoding='utf-8') as file:
            agendamentos_salvos = json.load(file)
            # Converte as strings de data/hora de volta para objetos datetime
            agendamentos = []
            for ag in agendamentos_salvos:
                ag['data_hora'] = datetime.strptime(ag['data_hora'], "%Y-%m-%d %H:%M")
                agendamentos.append(ag)
    else:
        agendamentos = []
        salvar_agendamentos()

def salvar_numeros():
    with open(NUMEROS_FILE, 'w', encoding='utf-8') as file:
        json.dump(NUMEROS_GRAVADOS, file, ensure_ascii=False, indent=4)

def salvar_mensagens():
    with open(MENSAGENS_FILE, 'w', encoding='utf-8') as file:
        json.dump(MENSAGENS_GRAVADAS, file, ensure_ascii=False, indent=4)

def salvar_agendamentos():
    with agendamentos_lock:
        try:
            # Converte as datas para string antes de salvar
            agendamentos_para_salvar = []
            for ag in agendamentos:
                ag_copy = ag.copy()
                if isinstance(ag_copy["data_hora"], datetime):
                    ag_copy["data_hora"] = ag_copy["data_hora"].strftime("%Y-%m-%d %H:%M")
                agendamentos_para_salvar.append(ag_copy)
                
            with open(AGENDAMENTOS_FILE, 'w', encoding='utf-8') as file:
                json.dump(agendamentos_para_salvar, file, ensure_ascii=False, indent=4)
            
            logging.info("Agendamentos salvos com sucesso")
        except Exception as e:
            logging.error(f"Erro ao salvar agendamentos: {e}")

# Inicializa os dados
carregar_dados()

# Inicializa arquivo de log se não existir
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Responsável", "Número", "Mensagem", "Data e Hora", "Status"])

def salvar_log(responsavel, numero, mensagem, data_hora, status):
    try:
        # Garante que o diretório de logs existe
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        # Verifica se o arquivo existe
        arquivo_existe = os.path.exists(LOG_FILE)
        
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Escreve o cabeçalho se o arquivo não existir
            if not arquivo_existe:
                writer.writerow(['Responsável', 'Número/Contato', 'Mensagem', 'Data/Hora', 'Status'])
            
            # Procura o nome do contato correspondente ao número
            nome_contato = next((contato['nome'] for contato in NUMEROS_GRAVADOS if contato['numero'] == numero), numero)
            
            # Escreve o log com o nome do contato
            writer.writerow([responsavel, nome_contato, mensagem, data_hora, status])
            
    except Exception as e:
        logging.error(f"Erro ao salvar log: {e}")

class WhatsAppError:
    def __init__(self, erro_type, mensagem, detalhes=None, timestamp=None):
        self.erro_type = erro_type
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "tipo": self.erro_type,
            "mensagem": self.mensagem,
            "detalhes": self.detalhes,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def from_dict(data):
        return WhatsAppError(
            data["tipo"],
            data["mensagem"],
            data["detalhes"],
            datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
        )

def salvar_erro(erro):
    try:
        erros_file = os.path.join(APP_DATA, 'logs', 'erros.json')
        erros = []
        
        # Carregar erros existentes
        if os.path.exists(erros_file):
            with open(erros_file, 'r', encoding='utf-8') as f:
                erros = json.load(f)
        
        # Adicionar novo erro
        erros.append(erro.to_dict())
        
        # Manter apenas os últimos 100 erros
        erros = erros[-100:]
        
        # Salvar erros
        with open(erros_file, 'w', encoding='utf-8') as f:
            json.dump(erros, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        logging.error(f"Erro ao salvar log de erro: {e}")

def extract_name_from_contact(contact_nome):
    """Extracts name from contact format like '2-volseg (Carlos)'"""
    try:
        # Look for text between parentheses
        import re
        match = re.search(r'\((.*?)\)', contact_nome)
        if match:
            return match.group(1)
        # If no parentheses, return the full name
        return contact_nome
    except:
        return contact_nome
        
def enviar_mensagem_whatsapp(numero, mensagem, nome_contato=None):
    try:
        if nome_contato:
            # Replace {{nome}} with the contact name
            mensagem = mensagem.replace("{{nome}}", nome_contato)
            
        logging.info(f"Iniciando envio para {numero}")

        # Exibe a mensagem de aviso usando notificação do sistema
        notification.notify(
            title='WhatsApp Agendador',
            message='Atenção! O PC será controlado!',
            app_icon=None,  # pode definir um ícone se desejar
            timeout=6,  # duração de 5 segundos
        )
        
        # Aguarda os 5 segundos da notificação
        time.sleep(6)

        # Defina o nome do perfil que deseja abrir
        profile_name = "Profile 1"  # Substitua pelo nome do seu perfil

        # Caminho padrão do Chrome no Windows (ajuste conforme necessário)
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        # Abre o Chrome com o perfil específico e captura o processo
        subprocess.Popen([chrome_path, f"--profile-directory={profile_name}"])

        time.sleep(2)  # Aguarda 2 segundos para abrir o Chrome 
        
        # Remove caracteres especiais e espaços
        numero = ''.join(filter(str.isdigit, numero))
        
        # Adiciona o código do país se não existir
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Adiciona o + no início
        numero = '+' + numero

        time.sleep(2)  # Aguarda 2 segundos para abrir o WhatsApp Web       

        # Registra tentativa
        erro = WhatsAppError(
            "TENTATIVA_ENVIO",
            f"Iniciando envio para {numero}",
            {
                "numero": numero,
                "mensagem": mensagem
            }
        )
        salvar_erro(erro)

        # Tenta enviar a mensagem
        kit.sendwhatmsg_instantly(
            numero,
            mensagem,
            wait_time=15,
            tab_close=False  # Desativado para melhor controle
        )
        
        # Aguarda para garantir que a mensagem foi enviada
        time.sleep(5)
        
        # Encerra apenas a instância do Chrome que foi aberta para o envio
        try:
            pyautogui.hotkey('alt', 'f4')
            logging.info("Instância do Chrome encerrada com Alt+F4.")

            time.sleep(1)  # Aguarda 1 segundo  

            # pyautogui.hotkey('Enter')
            # logging.info("Enter para fechar pop-up")
        except Exception as ex:
            logging.error(f"Falha ao fechar via Alt+F4: {ex}")

        # Considera a mensagem como enviada se chegou até aqui
        erro = WhatsAppError(
            "ENVIO_SUCESSO",
            f"Mensagem enviada com sucesso para {numero}",
            {"numero": numero}
        )
        salvar_erro(erro)
        logging.info(f"Mensagem enviada com sucesso para {numero}")
        return True
            
    except Exception as e:
        erro = WhatsAppError(
            "ERRO_ENVIO",
            f"Erro ao enviar mensagem para {numero}",
            {
                "numero": numero,
                "erro": str(e),
                "tipo_erro": type(e).__name__
            }
        )
        salvar_erro(erro)
        logging.error(f"Erro ao enviar mensagem para {numero}: {e}")
        return False

def verificar_agendamentos():
    while True:
        try:
            now = datetime.now()
            agendamentos_processados = set()
            
            for agendamento in agendamentos:
                agendamento_key = f"{agendamento['responsavel']}_{agendamento['numero']}_{agendamento['data_hora'].strftime('%Y-%m-%d %H:%M')}"
                
                if (agendamento["status"] == "Pendente" and 
                    now >= agendamento["data_hora"] and 
                    agendamento_key not in agendamentos_processados):
                    
                    logging.info(f"Processando agendamento: {agendamento_key}")
                    agendamentos_processados.add(agendamento_key)
                    
                    try:
                        # Marca como em processamento para evitar duplicação
                        agendamento["status"] = "Em Processamento"
                        salvar_agendamentos()
                        
                        # Encontra o contato e extrai o nome
                        contato = next((c for c in NUMEROS_GRAVADOS if c["numero"] == agendamento["numero"]), None)
                        nome_contato = extract_name_from_contact(contato["nome"]) if contato else ""
                        
                        # Prepara a mensagem com o nome do contato
                        mensagem_formatada = agendamento["mensagem"].replace("{{nome}}", nome_contato)
                        
                        # Tenta enviar a mensagem
                        if enviar_mensagem_whatsapp(agendamento["numero"], mensagem_formatada):
                            agendamento["status"] = "Enviada"
                            salvar_log(
                                agendamento["responsavel"],
                                agendamento["numero"],
                                mensagem_formatada,  # Usa a mensagem formatada no log
                                agendamento["data_hora"].strftime("%Y-%m-%d %H:%M"),
                                "Enviada"
                            )
                            logging.info(f"Agendamento concluído com sucesso: {agendamento_key}")
                        else:
                            agendamento["status"] = "Erro: Falha no envio"
                            salvar_log(
                                agendamento["responsavel"],
                                agendamento["numero"],
                                mensagem_formatada,  # Usa a mensagem formatada no log
                                agendamento["data_hora"].strftime("%Y-%m-%d %H:%M"),
                                "Erro: Falha no envio"
                            )
                    except Exception as e:
                        erro_msg = str(e)
                        logging.error(f"Erro no agendamento {agendamento_key}: {erro_msg}")
                        agendamento["status"] = f"Erro: {erro_msg}"
                        salvar_log(
                            agendamento["responsavel"],
                            agendamento["numero"],
                            agendamento["mensagem"],  # Usa mensagem original em caso de erro
                            agendamento["data_hora"].strftime("%Y-%m-%d %H:%M"),
                            f"Erro: {erro_msg}"
                        )
                    finally:
                        salvar_agendamentos()
                        time.sleep(5)  # Aguarda entre processamentos
            
        except Exception as e:
            logging.error(f"Erro na verificação de agendamentos: {e}")
        
        time.sleep(30)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "adicionar_numero" in request.form:
            nome = request.form["nome"]
            numero = request.form["numero"]
            if nome and numero:
                NUMEROS_GRAVADOS.append({"nome": nome, "numero": numero})
                salvar_numeros()
            return redirect(url_for("index"))

        if "adicionar_mensagem" in request.form:
            nova_mensagem = request.form["nova_mensagem"]
            if nova_mensagem:
                MENSAGENS_GRAVADAS.append(nova_mensagem)
                salvar_mensagens()
            return redirect(url_for("index"))

        # Processamento do agendamento
        try:
            responsavel = request.form.get("responsavel")
            numeros_input = request.form.get("numeros_input", "").strip()
            mensagem = request.form.get("mensagem_input") or request.form.get("mensagem_select")
            data = request.form.get("data")
            hora = request.form.get("hora")

            if not all([responsavel, numeros_input, mensagem, data, hora]):
                flash("Todos os campos são obrigatórios!", "error")
                return redirect(url_for("index"))

            # Processa múltiplos números
            numeros = [num.strip() for num in numeros_input.split('\n') if num.strip()]
            
            if not numeros:
                flash("Adicione pelo menos um número válido!", "error")
                return redirect(url_for("index"))

            # Criar data/hora do agendamento
            data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
            
            if data_hora < datetime.now():
                flash("A data e hora devem ser futuras!", "error")
                return redirect(url_for("index"))

            # Criar um agendamento para cada número
            for numero in numeros:
                novo_agendamento = {
                    "id": len(agendamentos) + 1,
                    "responsavel": responsavel,
                    "numero": numero,
                    "mensagem": mensagem,
                    "data_hora": data_hora,
                    "status": "Pendente"
                }
                agendamentos.append(novo_agendamento)
            
            salvar_agendamentos()
            
            flash(f"Agendamento criado com sucesso para {len(numeros)} número(s)!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"Erro ao criar agendamento: {str(e)}", "error")
            return redirect(url_for("index"))

    return render_template(
        "index.html",
        mensagens_gravadas=MENSAGENS_GRAVADAS,
        numeros_gravados=NUMEROS_GRAVADOS,
        agendamentos=agendamentos
    )

@app.route("/erros")
def erros():
    try:
        erros_file = os.path.join(APP_DATA, 'logs', 'erros.json')
        if os.path.exists(erros_file):
            with open(erros_file, 'r', encoding='utf-8') as f:
                erros = json.load(f)
        else:
            erros = []
        
        return render_template("erros.html", erros=erros)
    except Exception as e:
        logging.error(f"Erro ao carregar página de erros: {e}")
        return render_template("erros.html", erros=[])

@app.route("/logs")
def logs():
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = 10  # registros por página
        
        # Criar um dicionário para mapear números a nomes
        numero_para_nome = {contato['numero']: contato['nome'] for contato in NUMEROS_GRAVADOS}
        
        todos_logs = []
        
        # Carrega os logs do arquivo
        with open(LOG_FILE, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Pula o cabeçalho
            for log in reader:
                if len(log) >= 5:  # Verifica se a linha tem todos os campos necessários
                    log_modificado = list(log)
                    log_modificado[1] = numero_para_nome.get(log[1], log[1])
                    todos_logs.append(log_modificado)
        
        # Ordena por data e hora (índice 3), mais recentes primeiro
        todos_logs.sort(key=lambda x: datetime.strptime(x[3], "%Y-%m-%d %H:%M"), reverse=True)
        
        # Calcula a paginação
        total_logs = len(todos_logs)
        total_pages = (total_logs + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Obtém logs da página atual
        logs_paginados = todos_logs[start_idx:end_idx]
        
        return render_template(
            "logs.html",
            logs=logs_paginados,
            agendamentos=agendamentos,
            numero_para_nome=numero_para_nome,
            current_page=page,
            total_pages=total_pages,
            total_logs=total_logs
        )
        
    except Exception as e:
        logging.error(f"Erro ao carregar logs: {str(e)}")
        return render_template("logs.html", logs=[], agendamentos=[], numero_para_nome={})

@app.route("/limpar_historico", methods=["POST"])
def limpar_historico():
    try:
        # Cria backup antes de limpar
        backup_file = os.path.join(os.path.dirname(LOG_FILE), 
                                 f'envios_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        # Copia o arquivo atual para backup
        if os.path.exists(LOG_FILE):
            import shutil
            shutil.copy2(LOG_FILE, backup_file)
        
        # Reinicia o arquivo de logs mantendo apenas o cabeçalho
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Responsável", "Número", "Mensagem", "Data e Hora", "Status"])
        
        # Limpa também os agendamentos concluídos
        global agendamentos
        agendamentos = [ag for ag in agendamentos if ag["status"] == "Pendente"]
        salvar_agendamentos()
        
        flash("Histórico de mensagens foi limpo com sucesso! Um backup foi criado.", "success")
    except Exception as e:
        flash(f"Erro ao limpar histórico: {str(e)}", "error")
    
    return redirect(url_for('logs'))

#novas rotas
@app.route("/excluir_numero/<int:index>")
def excluir_numero(index):
    if 0 <= index < len(NUMEROS_GRAVADOS):
        del NUMEROS_GRAVADOS[index]
        salvar_numeros()
    return redirect(url_for('index'))

@app.route("/excluir_mensagem/<int:index>")
def excluir_mensagem(index):
    if 0 <= index < len(MENSAGENS_GRAVADAS):
        del MENSAGENS_GRAVADAS[index]
        salvar_mensagens()
    return redirect(url_for('index'))

@app.route("/cancelar_agendamento/<int:id>")
def cancelar_agendamento(id):
    for agendamento in agendamentos:
        if agendamento["id"] == id and agendamento["status"] == "Pendente":
            agendamento["status"] = "Cancelado"
            salvar_agendamentos()
            break
    return redirect(url_for('logs'))

@app.route("/agendar", methods=["POST"])
def agendar():
    try:
        responsavel = request.form.get("responsavel")
        numeros = request.form.get("numeros_input").split('\n')
        mensagem = request.form.get("mensagem_input")
        data = request.form.get("data")
        hora = request.form.get("hora")
        
        # Validação básica
        if not all([responsavel, numeros, mensagem, data, hora]):
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for("index"))
        
        # Filtrar números vazios e remover espaços
        numeros = [num.strip() for num in numeros if num.strip()]
        
        if not numeros:
            flash("Adicione pelo menos um número válido!", "error")
            return redirect(url_for("index"))
        
        # Criar data/hora do agendamento
        data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
        
        if data_hora < datetime.now():
            flash("A data e hora devem ser futuras!", "error")
            return redirect(url_for("index"))
        
        # Criar um agendamento para cada número
        for numero in numeros:
            novo_agendamento = {
                "id": len(agendamentos) + 1,
                "responsavel": responsavel,
                "numero": numero,
                "mensagem": mensagem,
                "data_hora": data_hora,
                "status": "Pendente"
            }
            agendamentos.append(novo_agendamento)
        
        salvar_agendamentos()
        
        flash(f"Agendamento criado com sucesso para {len(numeros)} número(s)!", "success")
        return redirect(url_for("index"))
        
    except Exception as e:
        flash(f"Erro ao criar agendamento: {str(e)}", "error")
        return redirect(url_for("index"))
    
@app.route('/debug')
def debug():
    import os
    template_folder = app.template_folder
    templates = os.listdir(template_folder) if os.path.exists(template_folder) else []
    
    return {
        'template_folder': template_folder,
        'templates': templates,
        'working_directory': os.getcwd(),
        'absolute_template_path': os.path.abspath(template_folder)
    }
    
class WhatsAppSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Scheduler")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # Configurar ícone
        self.icon_path = os.path.join(APP_DATA, "whatsapp_icon.png")
        self.ensure_icon_exists()
        
        self.icon_image = Image.open(self.icon_path)
        self.icon_photo = ImageTk.PhotoImage(self.icon_image)
        self.root.iconphoto(True, self.icon_photo)

        # Criar interface
        self.create_gui()
        
        # Inicializar systray
        self.setup_systray()

    def ensure_icon_exists(self):
        """Garante que o ícone existe no diretório de dados do aplicativo"""
        if not os.path.exists(self.icon_path):
            # Criar um ícone verde básico
            img = Image.new('RGB', (64, 64), color='green')
            try:
                img.save(self.icon_path)
            except Exception as e:
                logging.error(f"Erro ao criar ícone: {e}")
                # Se não conseguir criar o ícone, usa um ícone em memória
                self.icon_image = img
                return
        
        try:
            self.icon_image = Image.open(self.icon_path)
        except Exception as e:
            logging.error(f"Erro ao abrir ícone: {e}")
            # Se não conseguir abrir o ícone, cria um em memória
            self.icon_image = Image.new('RGB', (64, 64), color='green')

    def create_gui(self):
        # Container principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="WhatsApp Agendador",
            font=('Helvetica', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # Status
        self.status_label = ttk.Label(
            main_frame,
            text="ATIVO",
            font=('Helvetica', 10, 'bold'),
            foreground='green'
        )
        self.status_label.pack(pady=(0, 15))

        # Botões
        ttk.Button(
            main_frame,
            text="Gerenciar Agendamentos",
            command=self.open_scheduler
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            main_frame,
            text="Minimizar para Bandeja",
            command=self.minimize_to_tray
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            main_frame,
            text="Parar",
            command=self.stop_server
        ).pack(fill=tk.X, pady=2)

    def setup_systray(self):
        menu = (
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Gerenciar", self.open_scheduler),
            pystray.MenuItem("Sair", self.stop_server)
        )
        self.icon = pystray.Icon(
            "whatsapp_scheduler",
            self.icon_image,
            "WhatsApp Scheduler",
            menu
        )

    def open_scheduler(self):
        webbrowser.open('http://localhost:5000')

    def minimize_to_tray(self):
        self.root.withdraw()

        # Criar o ícone apenas quando necessário
        menu = (
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Gerenciar", self.open_scheduler),
            pystray.MenuItem("Sair", self.stop_server)
        )
        self.icon = pystray.Icon("whatsapp_scheduler", self.icon_image, "WhatsApp Scheduler", menu)

        self.icon.run()

    def show_window(self):
        self.icon.stop()
        self.root.deiconify()

    def stop_server(self):
        global server_running
        server_running = False
        self.root.quit()
        os._exit(0)

def main():
    # Iniciar thread do Flask
    flask_thread = threading.Thread(target=app.run, kwargs={
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False,
        'use_reloader': False
    })
    flask_thread.daemon = True
    flask_thread.start()

    # Iniciar thread de verificação de agendamentos
    checker_thread = threading.Thread(target=verificar_agendamentos)
    checker_thread.daemon = True
    checker_thread.start()

    # Iniciar interface gráfica
    root = tk.Tk()
    app_gui = WhatsAppSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
    