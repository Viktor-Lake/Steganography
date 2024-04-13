import cv2 as cv
import argparse
import sys

def get_bit_planes(img):
    bit_plane = []
    for bit in range(8):
        plane = (img >> bit) & 1
        bit_plane.append(plane)
    return bit_plane

def unify_bit_planes(bit_planes):
    for i in range(len(bit_planes)):
        bit_planes[i] = bit_planes[i] << i
    return sum(bit_planes)

def read_n_bits(color_planes, n, bit_shift, size, shape, plano_bits):
    bits = []
    num_colors = len(color_planes)
    for i in range(n):
        i = i + bit_shift
        plane_index = i // (size*num_colors)
        color_index = i % num_colors
        x = (i // num_colors) % shape[1]
        y = (i // num_colors) // shape[1] % shape[0]
        #print(color_index, plane_index, x, y)
        bits.append(color_planes[color_index][plano_bits[plane_index]][y][x])
    return bits
    
def decodificar(imagem, plano_bits, texto_saida):
    # Verificar se o plano de bits é válido
    for bit in plano_bits:
        if bit < 0 or bit > 7:
            sys.exit("O plano de bits deve ser um número entre 0 e 7.")
    
    # Carregar a imagem 
    img = cv.imread(imagem)

    # Verificar se a imagem foi carregada corretamente
    if img is None:
        sys.exit("Não foi possível carregar a imagem.")
    
    # Dividir os canais de cor da imagem
    B, G, R = cv.split(img)

    # Receber os planos de bits individualmente
    B_planes = get_bit_planes(B)
    G_planes = get_bit_planes(G)
    R_planes = get_bit_planes(R)
    color_planes = [B_planes, G_planes, R_planes]

    # Ler tamanho da mensagem no cabeçalho
    plano_bits = list(set(plano_bits))
    tamanho_mensagem = read_n_bits(color_planes, 32, 0, B.size, B.shape, plano_bits)
    print(tamanho_mensagem)
    tamanho_mensagem = int("".join(str(bit) for bit in tamanho_mensagem), 2)
    print(tamanho_mensagem)

    # Ler a mensagem
    bits_mensagem = read_n_bits(color_planes, tamanho_mensagem, 32, B.size, B.shape, plano_bits)

    # Transformar a mensagem em texto
    mensagem = "".join(str(bit) for bit in bits_mensagem)
    mensagem = [mensagem[i:i+8] for i in range(0, len(mensagem), 8)]
    mensagem = [chr(int(byte, 2)) for byte in mensagem]
    mensagem = "".join(mensagem)

    # Salvar a mensagem em um arquivo de texto
    with open(texto_saida, "w") as f:
        f.write(mensagem)
    return 0

def main():
    parser = argparse.ArgumentParser(description="Decodificar uma mensagem de uma imagem.")
    parser.add_argument("imagem", type=str, help="Caminho da imagem com a mensagem codificada.")
    parser.add_argument("plano_de_bits", nargs="+", type=int, help="Plano de bits onde a mensagem foi codificada.")
    parser.add_argument("texto_saida", type=str, help="Caminho do arquivo de texto onde a mensagem será salva.")
    args = parser.parse_args()
    decodificar(args.imagem, args.plano_de_bits, args.texto_saida)
    return 0
    
if __name__ == "__main__":
    main() 
