import numpy as np
import cv2 as cv
import argparse
import sys

def convert_text_to_bits(text):
    with open(text, 'r') as file:
        text_string = file.read()
    bits = []
    for char in text_string:
        binary_char = format(ord(char), '08b')
        for bit in binary_char:
            bits.append(bit)
    return bits

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
    
def codificar(imagem, texto, plano_bits, imagem_saida):
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

    # Mostrar a imagem original e em cada canal de cor
    #cv.imshow("Original", img)
    #cv.imshow("Red", cv.merge([np.zeros_like(R), np.zeros_like(R), R]))
    #cv.imshow("Green", cv.merge([np.zeros_like(G), G, np.zeros_like(G)]))
    #cv.imshow("Blue", cv.merge([B, np.zeros_like(B), np.zeros_like(B)]))
    #cv.waitKey(0)

    # Receber os planos de bits individualmente
    B_planes = get_bit_planes(B)
    G_planes = get_bit_planes(G)
    R_planes = get_bit_planes(R)
    color_planes = [B_planes, G_planes, R_planes]

    #cv.imshow("Plano1B", B_planes[0])
    #cv.imshow("Plano1G", G_planes[0])
    #cv.imshow("Plano1R", R_planes[0])
    #cv.waitKey(0)

    # Transformar o texto em uma lista de bits
    bits = convert_text_to_bits(texto)

    # Verificar se a imagem tem espaço suficiente para o texto
    plano_bits = list(set(plano_bits))
    if len(bits) + 32 > B.size*len(plano_bits)*3:
        sys.exit("A imagem não tem espaço suficiente para o texto.")

    print(len(bits))

    # Codificar cabeçalho
    num_colors = len(color_planes)
    header = format(len(bits), '032b')
    for i, bit in enumerate(header):
        plane_index = i // (B.size*num_colors)
        color_index = i % num_colors
        x = (i // num_colors) % B.shape[1]
        y = (i // num_colors) // B.shape[1] % B.shape[0]
        color_planes[color_index][plano_bits[plane_index]][y][x] = int(bit)

    # Codificar o texto na imagem
    for i, bit in enumerate(bits):
        i = i + len(header)
        plane_index = i // (B.size*num_colors)
        color_index = i % num_colors
        x = (i // num_colors) % B.shape[1]
        y = (i // num_colors) // B.shape[1] % B.shape[0]
        color_planes[color_index][plano_bits[plane_index]][y][x] = int(bit)

    cv.imshow("Plano0G", G_planes[0]*255)
    cv.imshow("Plano1G", G_planes[1]*255)
    #cv.imshow("Plano2G", G_planes[2]*255)
    cv.imshow("Plano7G", G_planes[7]*255)
    cv.waitKey(0)
    
    # Reunir os planos de bits
    B = unify_bit_planes(B_planes)
    G = unify_bit_planes(G_planes)
    R = unify_bit_planes(R_planes)

    # Juntar os canais de cor
    img_final = cv.merge([B, G, R])
    cv.imshow("input", img)
    cv.imshow("Final", img_final)
    cv.waitKey(0)

    # Salvar a imagem
    cv.imwrite(imagem_saida, img_final)

def main():
    parser = argparse.ArgumentParser(description='Esconder um texto em uma imagem')
    parser.add_argument('imagem', type=str, help='Caminho da imagem a ser modificada com o texto.')
    parser.add_argument('texto', type=str, help='Texto a ser codificado.')
    parser.add_argument("plano_bits", nargs='+', type=int, help='Plano de bits a ser utilizado para codificar o texto.')
    parser.add_argument("imagem_saida", type=str, help='Caminho da imagem de saída.')
    args = parser.parse_args()
    codificar(args.imagem, args.texto, args.plano_bits, args.imagem_saida)
    return 0

if __name__ == "__main__":
    main() 
