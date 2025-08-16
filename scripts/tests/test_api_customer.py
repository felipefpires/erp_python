import requests
import json

# --- Configuração ---
BASE_URL = "http://192.168.18.191:5000"
API_ENDPOINT = f"{BASE_URL}/crm/api/customers"

# --- Dados do Cliente de Teste ---
new_customer_data = {
    "name": "Cliente de Teste API",
    "email": "teste.api@example.com",
    "phone": "999998888",
    "instagram": "teste_api_insta",
    "address": "Rua dos Testes, 123",
    "city": "Cidade Teste",
    "state": "TS",
    "zip_code": "98765-432",
    "company": "Empresa de Testes",
    "cpf_cnpj": "12.345.678/0001-99",
    "status": "active"
}

def test_create_and_list_customers():
    """
    Testa a criação de um novo cliente e a listagem de clientes via API.
    """
    # --- 1. Criar um novo cliente ---
    print("--- TENTANDO CRIAR NOVO CLIENTE ---")
    try:
        response_post = requests.post(API_ENDPOINT, json=new_customer_data)
        
        # Verificar se o request POST foi bem-sucedido
        if response_post.status_code == 201:
            created_customer = response_post.json()
            print("✅ Cliente criado com sucesso!")
            print(json.dumps(created_customer, indent=2))
        else:
            print(f"❌ Erro ao criar cliente. Código de Status: {response_post.status_code}")
            print("Resposta do servidor:")
            print(response_post.text)
            return

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na conexão ao tentar criar cliente: {e}")
        return

    print("\n" + "="*40 + "\n")

    # --- 2. Listar todos os clientes ---
    print("--- TENTANDO LISTAR CLIENTES ---")
    try:
        response_get = requests.get(API_ENDPOINT)

        # Verificar se o request GET foi bem-sucedido
        if response_get.status_code == 200:
            customers = response_get.json()
            print(f"✅ Sucesso! {len(customers)} cliente(s) encontrado(s).")
            
            if customers:
                print("--- Lista de Clientes ---")
                print(json.dumps(customers, indent=2))
            else:
                print("ℹ️ A lista de clientes está vazia.")
        else:
            print(f"❌ Erro ao listar clientes. Código de Status: {response_get.status_code}")
            print("Resposta do servidor:")
            print(response_get.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na conexão ao tentar listar clientes: {e}")

    print("\n" + "="*40 + "\n")

    # --- 3. Buscar o cliente específico pelo nome ---
    print("--- TENTANDO BUSCAR CLIENTE POR NOME ---")
    customer_name_to_search = new_customer_data["name"]
    # URL encode the customer name to handle spaces and special characters
    encoded_customer_name = requests.utils.quote(customer_name_to_search)
    search_url = f"{API_ENDPOINT}/{encoded_customer_name}"
    
    try:
        response_search = requests.get(search_url)

        if response_search.status_code == 200:
            customer = response_search.json()
            print(f"✅ Cliente '{customer_name_to_search}' encontrado com sucesso!")
            print(json.dumps(customer, indent=2))
        elif response_search.status_code == 404:
            print(f"❌ Cliente '{customer_name_to_search}' não encontrado.")
        else:
            print(f"❌ Erro ao buscar cliente. Código de Status: {response_search.status_code}")
            print("Resposta do servidor:")
            print(response_search.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na conexão ao tentar buscar cliente: {e}")


if __name__ == "__main__":
    test_create_and_list_customers()