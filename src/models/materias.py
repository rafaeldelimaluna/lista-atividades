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
        value = value.lower()
        if value.__contains__(Materias.Matematica.lower()):
            return Materias.Matematica
        if value.__contains__(Materias.Fisica.lower()):
            return Materias.Fisica
        if value.__contains__(Materias.Quimica.lower()):
            return Materias.Quimica
        if value.__contains__(Materias.Historia.lower()):
            return Materias.Historia
        if value.__contains__(Materias.Geografia.lower()):
            return Materias.Geografia
        if value.__contains__(Materias.Portugues.lower()):
            return Materias.Portugues
        if value.__contains__(Materias.Literatura.lower()):
            return Materias.Literatura
        if value.__contains__(Materias.InterpretacaoDeTexto.lower()):
            return Materias.InterpretacaoDeTexto
        if value.__contains__(Materias.Redacao.lower()):
            return Materias.Redacao
        if value.__contains__(Materias.Gramatica.lower()):
            return Materias.Gramatica
        if value.__contains__(Materias.Ingles.lower()):
            return Materias.Ingles
        if value.__contains__(Materias.FilosofiaSociologia[0].lower() or Materias.FilosofiaSociologia[1].lower()):
            return Materias.FilosofiaSociologia
        if value.__contains__(Materias.Biologia.lower()):
            return Materias.Biologia
        return Materias.Geral


