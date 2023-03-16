from machine import automata as aut
from machine import nza_parser as nza


def main():
    # Load the plant files
    product = nza.directory_parser(
        '/home/mauricio/automata_to_st/product', True)
    # Load supervisor controllers files
    supervisors = nza.directory_parser(
        '/home/mauricio/automata_to_st/supervisors', False)
    # Join the product system and its supervisor controllers
    automata = product+supervisors

    # Generate the structured text corresponding to the system to be implemented
    A, B = aut.variableInitialization(automata)
    C, D, F, G = aut.transitionsDeclaration(automata)
    E = aut.disablementsDeclaration(automata)

    # Write the supervisor controller in a .txt file in the main folder
    f = open('results/st_modular_supervisor.txt', 'w')
    f.write(A)
    f.write(B)
    f.write(C)
    f.write(D)
    f.write(E)
    f.write(F)
    f.write(G)
    f.close()
    print('Modular supervisor generated in file: st_modular_supervisor.txt.')
    print('Dont forget to implement callback functions at the end of the file')


if __name__ == "__main__":
    main()
