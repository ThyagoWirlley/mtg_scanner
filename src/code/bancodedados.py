import requests
import os
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
import io

# Função para gerar embeddings usando um modelo pré-treinado
def generate_embedding(image_data):
    # Carregar modelo pré-treinado (ResNet50, por exemplo)
    model = models.resnet50(pretrained=True)
    model.eval()  # Colocar o modelo em modo de avaliação

    # Definir as transformações que serão aplicadas à imagem
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Abrir a imagem usando PIL e aplicar as transformações
    image = Image.open(io.BytesIO(image_data))
    image = transform(image).unsqueeze(0)  # Adicionar batch dimension

    # Passar a imagem pelo modelo para obter o embedding
    with torch.no_grad():
        embedding = model(image).squeeze().cpu().numpy()

    return embedding

# Função para pegar as cartas de Pokémon e suas imagens de diferentes idiomas
def fetch_card_images():
    # URL base da API (sem especificar o idioma)
    base_url = "https://api.tcgdex.net/v2/{}/cards/"

    # Idiomas disponíveis
    idiomas = [
        "en", "fr", "es", "it", "pt", "pt-br", "pt-pt", "de", "nl", "pl", 
        "ru", "ja", "ko", "zh-tw", "id", "th", "zh-cn"
    ]

    # Criar um diretório para armazenar as imagens
    os.makedirs("cartas_imagens", exist_ok=True)

    # Dicionário para armazenar os embeddings
    all_embeddings = {}

    # Exemplo de carta (substituir pelo ID correto da carta que você deseja buscar)
    card_id = "swsh3-136"  # ID da carta

    # Iterar sobre cada idioma e pegar as cartas
    for idioma in idiomas:
        print(f"Buscando cartas no idioma: {idioma}")

        # Construir a URL para pegar as informações da carta
        response = requests.get(f"{base_url.format(idioma)}{card_id}")
        
        if response.status_code == 200:
            card = response.json()

            # URL da imagem com qualidade e extensão
            image_url = f"https://assets.tcgdex.net/{idioma}/swsh/swsh3/{card['localId']}/high.jpg"  # Imagem em alta qualidade
            print(f"Buscando imagem da carta: {card['name']} com URL: {image_url}")
            
            # Nome do arquivo para a imagem
            image_filename = os.path.join("cartas_imagens", f"{card['name']}_{card['localId']}_{idioma}.jpg")
            
            # Baixar a imagem
            try:
                image_data = requests.get(image_url).content
                with open(image_filename, "wb") as file:
                    file.write(image_data)
                print(f"Imagem da carta '{card['name']}' salva com sucesso em {image_filename}")
                
                # Gerar o embedding da imagem
                embedding = generate_embedding(image_data)

                # Adicionar o embedding ao dicionário (usando o ID da carta e idioma como chave)
                all_embeddings[f"{card['localId']}_{idioma}"] = embedding

                # Apagar a imagem após o processamento
                os.remove(image_filename)
                print(f"Imagem da carta '{card['name']}' deletada após o processamento.")
                
            except Exception as e:
                print(f"Erro ao baixar a imagem da carta '{card['name']}': {e}")
        else:
            print(f"Erro ao buscar a carta com ID {card_id} no idioma {idioma}: {response.status_code}")

    # Após processar todas as cartas, salvar os embeddings em um arquivo
    embeddings_filename = "cartas_embeddings.npy"
    np.save(embeddings_filename, all_embeddings)
    print(f"Embeddings salvos no arquivo: {embeddings_filename}")

# Chamar a função para baixar as imagens e gerar os embeddings
fetch_card_images()
