import httpx
import sys

# NEXUS CORE Endpoint
BASE_URL = "http://localhost:8000"

# Mapeamento de Teclas para Comandos Soberanos
MACROS = {
    'a': "/APOGEU",
    'c': "/CARRASCO",
    's': "/SOBERANIA",
    'e': "/EVOLUIR",
    'm': "/MUTAR",
    'h': "/HARVEST",
    'z': "/SINTETIZAR"
}

def send_command(command):
    """Envia o comando para o Nexus Core."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{BASE_URL}/command", json={"command": command})
            if response.status_code == 200:
                res_data = response.json()
                print(f"\n[OK] {command} executado com sucesso.")
                print(f"Resposta: {res_data.get('message', res_data)}")
            else:
                print(f"\n[ERRO] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"\n[FALHA DE CONEXÃO] Não foi possível contatar o Nexus Core em {BASE_URL}")
        print(f"Detalhe: {e}")

def show_menu():
    print("\n" + "="*40)
    print("   IMPÉRIO-MUTANTE - MACROS CLI v1.0")
    print("="*40)
    for key, cmd in MACROS.items():
        print(f" [{key.upper()}] -> {cmd}")
    print(" [Q] -> Sair")
    print("="*40)

def main():
    show_menu()
    while True:
        try:
            choice = input("\nSelecione um gatilho: ").lower()
            if choice == 'q':
                print("Encerrando macros.")
                break
            if choice in MACROS:
                send_command(MACROS[choice])
            else:
                print("Tecla inválida. Tente novamente.")
        except KeyboardInterrupt:
            print("\nEncerrando.")
            break

if __name__ == "__main__":
    main()
