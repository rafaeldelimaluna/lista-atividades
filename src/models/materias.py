class Materias:
    Matematica = "Mat"
    Fisica = "Fis"
    Quimica = "Quim"
    Historia = "Hist"
    Geografia = "Geo"
    Portugues = "Port"
    Literatura = "Lit"
    InterpretacaoDeTexto = "Inter"
    Redacao = "Red"
    Gramatica = "Gram"
    Ingles = "Ing"
    FilosofiaSociologia = ["Soc","Fil"]
    Biologia = "Bio"
    Geral = "Geral"

    def searchMateria(value:str)->str:
        """Essa classe tenta encontrar uma matéria escrita parcialmente, através da abreviação. \n
        Exemplo: value = Matemática, será retornado **Mat**, pois **Matemática** está contido em **Mat** \n
        Caso nenhum valor seja encontrado, é retornado **Geral**"""
        value = value.capitalize()
        if value.__contains__(Materias.Matematica):
            return Materias.Matematica
        if value.__contains__(Materias.Fisica):
            return Materias.Fisica
        if value.__contains__(Materias.Quimica):
            return Materias.Quimica
        if value.__contains__(Materias.Historia):
            return Materias.Historia
        if value.__contains__(Materias.Geografia):
            return Materias.Geografia
        if value.__contains__(Materias.Portugues):
            return Materias.Portugues
        if value.__contains__(Materias.Literatura):
            return Materias.Literatura
        if value.__contains__(Materias.InterpretacaoDeTexto):
            return Materias.InterpretacaoDeTexto
        if value.__contains__(Materias.Redacao):
            return Materias.Redacao
        if value.__contains__(Materias.Gramatica):
            return Materias.Gramatica
        if value.__contains__(Materias.Ingles):
            return Materias.Ingles
        if value.__contains__(Materias.FilosofiaSociologia[0] or Materias.FilosofiaSociologia[1]):
            return Materias.FilosofiaSociologia
        if value.__contains__(Materias.Biologia):
            return Materias.Biologia
        return Materias.Geral


