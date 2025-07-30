
WhatsApp Agendador - Sistema de Agendamento de Mensagens

DESCRIÇÃO:
Sistema completo para agendamento e envio automático de mensagens pelo WhatsApp. Inclui interface web para gerenciamento e aplicativo de bandeja do sistema.

PRINCIPAIS FUNCIONALIDADES:
- Agendamento de mensagens para múltiplos contatos
- Personalização de mensagens com o nome do contato
- Histórico completo de envios com logs detalhados
- Sistema de tratamento de erros robusto
- Interface web intuitiva (Flask)
- Ícone na bandeja do sistema para acesso rápido
- Notificações do sistema durante o envio
- Backup automático de logs

PRÉ-REQUISITOS:
- Python 3.9+
- Google Chrome instalado
- Conta do WhatsApp Web logada no Chrome (Perfil 1)
- Conexão com internet

INSTALAÇÃO:
1. Instale as dependências:
pip install pywhatkit flask pystray pillow plyer pyautogui

2. Execute o aplicativo:
python app.py

COMO USAR:
1. Após iniciar o app:
   - Janela principal mostrará status "ATIVO"
   - Clique em "Gerenciar Agendamentos" para abrir a interface web

2. Na interface web (http://localhost:5000):
   - CONTATOS: Adicione/remova números com nomes
   - MENSAGENS: Gerencie mensagens pré-definidas
   - AGENDAMENTOS: Crie novos agendamentos:
     • Responsável
     • Números (um por linha)
     • Mensagem (use {{nome}} para personalizar)
     • Data e hora
   - LOGS: Visualize histórico de envios
   - ERROS: Consulte problemas ocorridos

3. Controle pelo ícone na bandeja do sistema:
   - Botão direito para opções:
     • Mostrar: Restaura janela principal
     • Gerenciar: Abre interface web
     • Sair: Encerra aplicativo

FLUXO DE ENVIO:
1. Chegado o horário agendado:
   - Sistema mostra notificação "Atenção! O PC será controlado!"
   - Abre automaticamente o Chrome com perfil configurado
   - Envia mensagem pelo WhatsApp Web
   - Fecha a janela do Chrome após envio
   - Atualiza status no histórico

RECURSOS AVANÇADOS:
- Paginação de logs
- Backup automático ao limpar histórico
- Personalização de mensagens com {{nome}}
- Tentativas múltiplas em caso de falha
- Controle preciso do navegador

SOLUÇÃO DE PROBLEMAS:
- Envios não realizados:
  1. Verifique se o WhatsApp Web está logado no Chrome (Perfil 1)
  2. Confira os erros na interface web (/erros)
  3. Verifique permissões do antivírus

- Problemas de interface:
  1. Recarregue a página (http://localhost:5000)
  2. Reinicie o aplicativo

- Erros comuns:
  • "Atenção! O PC será controlado!" não aparece: Verifique notificações do sistema
  • Chrome não abre: Configure caminho correto no código
  • Mensagem não personalizada: Use {{nome}} no texto

OBSERVAÇÕES IMPORTANTES:
1. Mantenha o aplicativo em execução para agendamentos funcionarem
2. Não feche o ícone na bandeja do sistema
3. O computador deve estar ligado no horário agendado
4. Use números no formato: 5511999999999 (código país + DDD + número)

REQUIREMENTS.TXT:
pywhatkit==5.4
flask==2.3.2
pystray==0.19.4
pillow==10.1.0
plyer==2.1.0
pyautogui==0.9.54
openpyxl==3.1.2
pywinauto==0.6.8
pywin32==306
