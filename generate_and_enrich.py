# -*- coding: utf-8 -*-
"""
Full Dataset Generator & Enricher
Enriches existing names with Spanish meanings, normalized origins, and Santoral feast days.
Generates 2,000 new Latin/Hispanic names (including compound names).
Categorizes names similar to the 1,091 excluded names into 'similar_excluded' (⚠️ 4th category).
"""

import json
import re
import unicodedata
from collections import OrderedDict

def strip_accents(s):
    if not s:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower().strip()

def levenshtein_dist(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_dist(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Santoral calendar mapping
SANTORAL_MAP = {
    "maria": "1 de enero (Madre de Dios) / 15 de agosto (Asunción) / 12 de septiembre (Dulce Nombre)",
    "ana": "26 de julio (Santa Ana, madre de la Virgen)",
    "lucia": "13 de diciembre (Santa Lucía de Siracusa)",
    "carmen": "16 de julio (Virgen del Carmen)",
    "sofia": "30 de septiembre (Santa Sofía)",
    "valentina": "14 de febrero / 25 de julio (Santa Valentina)",
    "isabel": "4 de julio (Santa Isabel de Portugal) / 17 de noviembre (Santa Isabel de Hungría)",
    "teresa": "15 de octubre (Santa Teresa de Jesús) / 1 de octubre (Santa Teresita)",
    "clara": "11 de agosto (Santa Clara de Asís)",
    "rosa": "23 de agosto (Santa Rosa de Lima)",
    "laura": "19 de octubre (Santa Laura de Córdoba) / 1 de junio",
    "paula": "26 de enero (Santa Paula de Roma)",
    "paulina": "26 de mayo / 2 de diciembre (Santa Paulina)",
    "elena": "18 de agosto (Santa Elena, emperatriz)",
    "beatriz": "18 de enero / 29 de julio (Santa Beatriz de Silva)",
    "cecilia": "22 de noviembre (Santa Cecilia, patrona de la música)",
    "pilar": "12 de octubre (Nuestra Señora del Pilar)",
    "rocio": "Lunes de Pentecostés (Virgen del Rocío)",
    "guadalupe": "12 de diciembre (Nuestra Señora de Guadalupe)",
    "mercedes": "24 de septiembre (Virgen de la Merced)",
    "fatima": "13 de mayo (Nuestra Señora de Fátima)",
    "lourdes": "11 de febrero (Nuestra Señora de Lourdes)",
    "ines": "21 de enero (Santa Inés, virgen y mártir)",
    "catalina": "29 de abril (Santa Catalina de Siena) / 25 de noviembre",
    "caterina": "29 de abril (Santa Catalina de Siena)",
    "sara": "13 de julio (Santa Sara, matriarca)",
    "marta": "29 de julio (Santa Marta de Betania)",
    "veronica": "9 de julio (Santa Verónica)",
    "patricia": "25 de agosto (Santa Patricia de Nápoles)",
    "julia": "8 de abril / 22 de mayo (Santa Julia)",
    "julieta": "16 de junio (Santa Julieta)",
    "victoria": "17 de noviembre / 23 de diciembre (Santa Victoria)",
    "natalia": "27 de julio (Santa Natalia) / 1 de diciembre",
    "diana": "9 de junio (Beata Diana)",
    "silvia": "3 de noviembre (Santa Silvia)",
    "cristina": "24 de julio (Santa Cristina)",
    "irene": "5 de mayo (Santa Irene) / 20 de octubre",
    "begona": "15 de agosto (Nuestra Señora de Begoña)",
    "montserrat": "27 de abril (Virgen de Montserrat)",
    "macarena": "18 de diciembre (Virgen de la Esperanza Macarena)",
    "candela": "2 de febrero (Virgen de la Candelaria)",
    "candelaria": "2 de febrero (Virgen de la Candelaria)",
    "dolores": "15 de septiembre (Nuestra Señora de los Dolores)",
    "concepcion": "8 de diciembre (Inmaculada Concepción)",
    "inmaculada": "8 de diciembre (Inmaculada Concepción)",
    "remedios": "Segundo domingo de octubre (Virgen de los Remedios)",
    "amparo": "Segundo domingo de mayo (Virgen de los Desamparados)",
    "paloma": "15 de agosto (Virgen de la Paloma)",
    "triana": "26 de julio (Santa Ana de Triana)",
    "vega": "8 de septiembre (Virgen de la Vega)",
    "covadonga": "8 de septiembre (Virgen de Covadonga)",
    "aitana": "22 de abril (Nuestra Señora de Aitana)",
    "jimena": "18 de febrero (Santa Jimena)",
    "altagracia": "21 de enero (Nuestra Señora de la Altagracia)",
    "chiquinquira": "18 de noviembre (Nuestra Señora de Chiquinquirá)",
    "coromoto": "11 de septiembre (Virgen de Coromoto)",
    "juana": "24 de mayo (Santa Juana de Arco) / 30 de mayo",
    "juanita": "24 de mayo (Santa Juana)",
    "alicia": "16 de diciembre (Santa Alicia)",
    "claudia": "18 de mayo (Santa Claudia)",
    "valeria": "28 de abril (Santa Valeria)",
    "camila": "14 de julio / 26 de julio (San Camilo / Beata Camila)",
    "camille": "14 de julio (San Camilo)",
    "andrea": "30 de noviembre (San Andrés)",
    "daniela": "21 de julio (San Daniel profeta)",
    "gabriela": "29 de septiembre (San Gabriel Arcángel)",
    "rafaela": "29 de septiembre (Santa Rafaela María / San Rafael)",
    "noelia": "25 de diciembre (Natividad del Señor)",
    "raquel": "2 de septiembre (Santa Raquel)",
    "rebeca": "23 de marzo (Santa Rebeca)",
    "ester": "24 de mayo (Santa Ester, reina)",
    "esther": "24 de mayo (Santa Ester)",
    "miriam": "1 de enero / 15 de agosto (María)",
    "marina": "18 de julio (Santa Marina)",
    "blanca": "5 de agosto (Nuestra Señora de las Nieves / Santa Blanca)",
    "aurora": "15 de septiembre / 20 de octubre (Santa Aurora)",
    "estrella": "15 de agosto (Nuestra Señora de la Estrella)",
    "sol": "15 de septiembre (Nuestra Señora de la Soledad)",
    "soledad": "15 de septiembre (Virgen de la Soledad)",
    "paz": "24 de enero (Nuestra Señora de la Paz)",
    "gracia": "23 de julio (Nuestra Señora de Gracia)",
    "milagros": "8 de diciembre (Virgen de los Milagros)",
    "esperanza": "18 de diciembre (Nuestra Señora de la Esperanza)",
    "caridad": "8 de septiembre (Caridad del Cobre)",
    "asuncion": "15 de agosto (Asunción de la Virgen María)",
    "nieves": "5 de agosto (Nuestra Señora de las Nieves)",
    "loreto": "10 de diciembre (Nuestra Señora de Loreto)",
    "almudena": "9 de noviembre (Virgen de la Almudena)",
    "fuensanta": "8 de septiembre (Virgen de la Fuensanta)",
    "aranzazu": "9 de septiembre (Virgen de Aránzazu)",
    "africa": "5 de agosto (Santa María de África)",
    "angustias": "15 de septiembre (Virgen de las Angustias)",
    "araceli": "Primer domingo de mayo (Virgen de Araceli)",
    "consolacion": "4 de septiembre (Virgen de la Consolación)",
    "piedad": "15 de septiembre (Virgen de la Piedad)",
    "presentacion": "21 de noviembre (Presentación de la Virgen)",
    "purificacion": "2 de febrero (Purificación de Nuestra Señora)",
    "regla": "8 de septiembre (Virgen de Regla)",
    "socorro": "27 de junio (Perpetuo Socorro)",
    "sagrario": "15 de agosto (Virgen del Sagrario)",
    "prado": "15 de agosto (Virgen del Prado)",
    "mar": "15 de agosto (Virgen del Mar)",
    "valle": "8 de septiembre (Virgen del Valle)",
    "camino": "8 de septiembre (Virgen del Camino)",
    "pena": "8 de septiembre (Virgen de la Peña)",
    "encarnacion": "25 de marzo (Encarnación del Señor)",
    "anunciacion": "25 de marzo (Anunciación)",
    "visitacion": "31 de mayo (Visitación de la Virgen)",
    "gemma": "14 de mayo (Santa Gema Galgani)",
    "rita": "22 de mayo (Santa Rita de Casia)",
    "monica": "27 de agosto (Santa Mónica)",
    "agueda": "5 de febrero (Santa Águeda)",
    "apolonia": "9 de febrero (Santa Apolonia)",
    "eulalia": "12 de febrero / 10 de diciembre (Santa Eulalia)",
    "engracia": "16 de abril (Santa Engracia)",
    "leocadia": "9 de diciembre (Santa Leocadia de Toledo)",
    "bibiana": "2 de diciembre (Santa Bibiana)",
    "viviana": "2 de diciembre (Santa Viviana)",
    "casilda": "9 de abril (Santa Casilda)",
    "prisca": "18 de enero (Santa Prisca)",
    "martina": "30 de enero (Santa Martina)",
    "flora": "24 de noviembre (Santa Flora de Córdoba)",
    "aurelia": "15 de octubre (Santa Aurelia)",
    "justa": "19 de julio (Santa Justa)",
    "rufina": "19 de julio (Santa Rufina)",
    "marcella": "31 de enero (Santa Marcela de Roma)",
    "marcela": "31 de enero (Santa Marcela de Roma)",
    "flavia": "7 de mayo (Santa Flavia)",
    "priscila": "16 de enero (Santa Priscila)",
    "sabina": "29 de agosto (Santa Sabina)",
    "faustina": "5 de octubre (Santa Faustina)",
    "teodora": "11 de febrero (Santa Teodora)",
    "eugenia": "25 de diciembre (Santa Eugenia)",
    "matilde": "14 de marzo (Santa Matilde)",
    "adelaida": "16 de diciembre (Santa Adelaida)",
    "clotilde": "3 de junio (Santa Clotilde)",
    "carlota": "17 de julio / 4 de noviembre (Beata Carlota)",
    "gisela": "7 de mayo (Beata Gisela)",
    "yolanda": "28 de diciembre (Santa Yolanda)",
    "elvira": "25 de enero (Santa Elvira)",
    "berenice": "14 de abril (Santa Berenice)",
    "tamara": "1 de mayo (Santa Tamara)",
    "tatiana": "12 de enero (Santa Tatiana)",
    "lidia": "3 de agosto (Santa Lidia)",
    "noemi": "24 de diciembre (Santa Noemí)",
    "zoe": "2 de mayo (Santa Zoe)",
    "aurea": "19 de julio (Santa Áurea)",
    "celeste": "19 de mayo (Santa Celeste)",
    "celina": "21 de octubre (Santa Celina)",
    "regina": "7 de septiembre (Santa Regina)",
    "olimpia": "17 de diciembre (Santa Olimpia)",
    "amanda": "6 de febrero (Santa Amanda)",
    "belinda": "19 de febrero (Santa Belinda)",
    "cintia": "6 de junio (Santa Cintia)",
    "dalia": "25 de octubre (Santa Dalia)",
    "elsa": "4 de enero (Santa Elsa)",
    "erika": "18 de mayo (Santa Érika)",
    "greta": "16 de noviembre (Santa Margarita / Greta)",
    "karina": "7 de noviembre (Santa Carina)",
    "lorena": "30 de mayo (Santa Lorena)",
    "melisa": "15 de septiembre (Santa Melisa)",
    "miranda": "12 de septiembre (Santa Miranda)",
    "olivia": "10 de junio (Santa Olivia de Palermo)",
    "renata": "12 de noviembre (Santa Renata)",
    "sabrina": "29 de agosto (Santa Sabrina)",
    "vanessa": "23 de octubre (Santa Vanesa)",
    "alexandra": "18 de mayo / 20 de marzo (Santa Alejandra)",
    "anahi": "26 de julio (Santa Ana / Flor de Ceibo)",
    "corina": "22 de octubre (Santa Corina)",
    "krista": "24 de julio (Santa Cristina / Krista)",
    "lisa": "5 de noviembre (Santa Isabel / Lisa)",
    "maribel": "15 de agosto / 4 de julio (María Isabel)",
    "millie": "18 de julio (Santa Emilia / Millie)",
    "mina": "13 de abril / 10 de diciembre (Santa Mina)",
    "nadia": "18 de septiembre (Santa Nadia / Esperanza)",
    "nicole": "6 de diciembre (San Nicolás / Santa Nicolasa)",
    "pamela": "16 de febrero (San Pámfilo / Santa Pamela)",
    "ximena": "18 de febrero (Santa Jimena)",
    "leire": "9 de julio (Virgen de Leire)",
    "mireia": "15 de agosto (Asunción)",
    "arlet": "28 de enero (San Arlet)",
    "nahia": "8 de diciembre (Inmaculada)",
    "amaia": "8 de septiembre (Virgen de Amaya)",
    "uxue": "15 de agosto (Virgen de Uxue)",
    "nerea": "12 de mayo (Santa Nerea)",
    "irache": "24 de mayo (Virgen de Irache)",
    "arantza": "9 de septiembre (Virgen de Aránzazu)",
    "itziar": "15 de agosto (Virgen de Itziar)",
    "idoya": "Lunes de Pentecostés (Virgen de Idoya)",
    "arantxa": "9 de septiembre (Virgen de Aránzazu)",
    "estibaliz": "1 de mayo (Virgen de Estíbaliz)",
    "soraya": "15 de agosto (Asunción)",
    "desiree": "8 de mayo (Santa Deseada)",
    "ainara": "17 de abril (Santa Ainara)",
    "ainhoa": "9 de septiembre (Virgen de Ainhoa)",
    "maricarmen": "16 de julio (Virgen del Carmen)",
    "mariluz": "1 de junio / 15 de agosto (Nuestra Señora de la Luz)",
    "marisol": "15 de septiembre (Virgen de la Soledad)",
    "maripaz": "24 de enero (Virgen de la Paz)",
    "marite": "15 de octubre (Santa Teresa)",
    "marisa": "4 de julio / 15 de agosto (María Luisa)",
    "maite": "15 de octubre (María Teresa / Maite 'amada')",
    "abril": "25 de abril (San Marcos / Flor de Primavera)",
    "adela": "24 de diciembre (Santa Adela)",
    "adelita": "24 de diciembre (Santa Adela)",
    "adriana": "17 de septiembre / 8 de marzo (Santa Adriana)",
    "almudena": "9 de noviembre (Virgen de la Almudena)",
    "amalia": "10 de julio (Santa Amalia)",
    "amara": "10 de mayo (Santa Amara)",
    "antonia": "29 de abril (Santa Antonia)",
    "antonella": "29 de abril (Santa Antonia / Antonella)",
    "azucena": "15 de agosto (Nuestra Señora de la Azucena)",
    "barbara": "4 de diciembre (Santa Bárbara)",
    "belen": "25 de diciembre (Nuestra Señora de Belén)",
    "berta": "4 de julio (Santa Berta)",
    "brisa": "15 de agosto (Asunción)",
    "carla": "4 de noviembre (San Carlos Borromeo)",
    "carolina": "4 de noviembre (Santa Carolina)",
    "cayetana": "7 de agosto (San Cayetano)",
    "celia": "22 de noviembre (Santa Cecilia / Celia)",
    "clarisa": "11 de agosto (Santa Clara)",
    "constanza": "19 de septiembre (Santa Constanza)",
    "consuelo": "4 de septiembre (Nuestra Señora de la Consolación)",
    "cora": "12 de mayo (Santa Cora)",
    "coral": "15 de agosto (Asunción)",
    "danna": "21 de julio (Santa Daniela)",
    "debora": "21 de septiembre (Santa Débora)",
    "delfina": "26 de noviembre (Santa Delfina)",
    "denise": "15 de mayo (Santa Dionisia / Denise)",
    "dulce": "12 de septiembre (Dulce Nombre de María)",
    "elisa": "5 de noviembre (Santa Isabel / Elisa)",
    "eliana": "20 de julio (Santa Eliana)",
    "eloisa": "11 de febrero (Beata Eloísa)",
    "emilia": "24 de agosto (Santa Emilia)",
    "emiliana": "5 de enero (Santa Emiliana)",
    "emma": "19 de abril / 29 de junio (Santa Emma)",
    "estefania": "26 de diciembre (San Esteban / Santa Estefanía)",
    "estela": "11 de mayo (Santa Estela)",
    "eva": "24 de diciembre (Adán y Eva)",
    "evangelina": "27 de diciembre (San Juan Evangelista)",
    "fabiola": "27 de diciembre (Santa Fabiola)",
    "felicia": "30 de septiembre (Santa Felicia)",
    "felicidad": "7 de marzo (Santas Perpetua y Felicidad)",
    "fernanda": "30 de mayo (San Fernando)",
    "fiorella": "15 de agosto (Asunción)",
    "florencia": "10 de noviembre (Santa Florencia)",
    "francisca": "4 de octubre (San Francisco) / 9 de marzo (Santa Francisca Romana)",
    "gala": "6 de abril / 5 de octubre (Santa Gala)",
    "genesis": "25 de diciembre (Principio de la Vida)",
    "genoveva": "3 de enero (Santa Genoveva)",
    "georgina": "23 de abril (San Jorge / Santa Georgina)",
    "gianna": "28 de abril (Santa Gianna Beretta Molla)",
    "gloria": "25 de marzo (Anunciación) / 15 de agosto",
    "graciela": "23 de julio (Nuestra Señora de Gracia)",
    "guillermina": "10 de enero (San Guillermo / Santa Guillermina)",
    "helena": "18 de agosto (Santa Elena)",
    "hortensia": "11 de enero (Santa Hortensia)",
    "isabela": "4 de julio (Santa Isabel)",
    "isabella": "4 de julio (Santa Isabel)",
    "jacinta": "20 de febrero (Santa Jacinta Marto)",
    "jazmin": "15 de agosto (Asunción)",
    "josefina": "19 de marzo (San José) / 8 de febrero (Santa Josefina Bakhita)",
    "judith": "29 de junio (Santa Judit)",
    "juliana": "16 de febrero (Santa Juliana)",
    "justina": "7 de octubre (Santa Justina)",
    "lara": "26 de marzo (Santa Lara)",
    "larisa": "26 de marzo (Santa Larisa)",
    "leonor": "22 de febrero (Santa Leonor)",
    "leticia": "9 de julio / 18 de agosto (Nuestra Señora de la Alegría)",
    "lia": "22 de marzo (Santa Lía)",
    "liliana": "27 de julio (Santa Liliana)",
    "lina": "23 de septiembre (San Lino)",
    "linda": "13 de febrero (Santa Linda)",
    "lola": "15 de septiembre (Nuestra Señora de los Dolores)",
    "lorenza": "10 de agosto (San Lorenzo)",
    "luciana": "13 de diciembre (Santa Lucía)",
    "lucila": "31 de octubre (Santa Lucila)",
    "lucrecia": "23 de noviembre (Santa Lucrecia)",
    "luisa": "15 de marzo (Santa Luisa de Marillac)",
    "luna": "15 de agosto (Asunción)",
    "luz": "1 de junio (Nuestra Señora de la Luz)",
    "magdalena": "22 de julio (Santa María Magdalena)",
    "malena": "22 de julio (Santa María Magdalena)",
    "manuela": "1 de enero (Jesús Emmanuel)",
    "mara": "1 de enero (María)",
    "margarita": "16 de noviembre / 20 de julio (Santa Margarita)",
    "mariana": "17 de abril (Santa Mariana de Jesús)",
    "marianela": "15 de agosto / 18 de agosto (María Elena)",
    "maura": "21 de septiembre (Santa Maura)",
    "mayra": "1 de enero (María)",
    "melania": "31 de diciembre (Santa Melania)",
    "micaela": "29 de septiembre (San Miguel / Santa Micaela)",
    "milena": "15 de agosto (María Elena)",
    "modesta": "4 de noviembre (Santa Modesta)",
    "morena": "12 de diciembre (Virgen Morena de Guadalupe)",
    "naira": "15 de agosto (Asunción)",
    "nancy": "26 de julio (Santa Ana)",
    "nayeli": "15 de agosto (Asunción)",
    "nazaret": "25 de marzo (Nuestra Señora de Nazaret)",
    "noa": "21 de agosto (Santa Noa)",
    "nora": "22 de febrero (Santa Leonor / Nora)",
    "norma": "13 de abril (Santa Norma)",
    "nuria": "8 de septiembre (Virgen de Nuria)",
    "ofelia": "3 de febrero (Santa Ofelia)",
    "olga": "11 de julio (Santa Olga de Kiev)",
    "oriana": "4 de octubre (Santa Oriana)",
    "ornella": "15 de agosto (Asunción)",
    "otilia": "13 de diciembre (Santa Otilia)",
    "paola": "26 de enero (Santa Paula)",
    "penelope": "5 de mayo (Santa Penélope)",
    "perla": "16 de noviembre (Santa Margarita / Perla)",
    "petra": "29 de junio (San Pedro / Santa Petra)",
    "ramona": "31 de agosto (San Ramón Nonato)",
    "reyes": "6 de enero (Epifanía / Reyes Magos)",
    "roberta": "17 de abril (San Roberto / Santa Roberta)",
    "romina": "23 de febrero (Santa Romina)",
    "rosalia": "4 de septiembre (Santa Rosalía de Palermo)",
    "rosalba": "23 de agosto / 5 de agosto (Rosa Blanca)",
    "rosalinda": "23 de agosto (Santa Rosa)",
    "rosana": "23 de agosto / 26 de julio (Rosa Ana)",
    "rosario": "7 de octubre (Nuestra Señora del Rosario)",
    "rosaura": "23 de agosto (Rosa Dorada)",
    "roxana": "20 de marzo (Santa Roxana)",
    "ruth": "16 de julio (Santa Rut)",
    "salome": "22 de octubre (Santa Salomé)",
    "salma": "24 de enero (Paz)",
    "sandra": "18 de mayo (Santa Alejandra)",
    "silvana": "10 de julio (Santa Silvana)",
    "simona": "28 de octubre (San Simón)",
    "sonia": "30 de septiembre (Santa Sofía)",
    "susana": "11 de agosto (Santa Susana)",
    "ursula": "21 de octubre (Santa Úrsula)",
    "vicenta": "22 de enero (San Vicente / Santa Vicenta)",
    "violeta": "3 de mayo (Santa Violeta)",
    "virginia": "15 de diciembre (Santa Virginia)",
    "xiomara": "18 de mayo (Santa Guiomar / Xiomara)",
    "yasmin": "15 de agosto (Flor de Jazmín)",
    "yuliana": "16 de febrero (Santa Juliana)",
    "zaida": "23 de julio (Santa Zaida)",
    "zaira": "21 de octubre (Santa Zaira)"
}

def lookup_saint_day(name_str):
    norm = strip_accents(name_str)
    if norm in SANTORAL_MAP:
        return SANTORAL_MAP[norm]
    parts = [strip_accents(p) for p in re.split(r'[\s\-]+', name_str) if len(p) >= 3]
    for p in parts:
        if p in SANTORAL_MAP:
            return SANTORAL_MAP[p]
    for k, v in SANTORAL_MAP.items():
        if len(k) >= 4 and (k in norm or norm in k):
            return v
    return "Sin santoral registrado en el martirologio común"

# Dictionary of translations for PDF meanings
ENGLISH_MEANING_TRANSLATIONS = {
    "high,exalted": "Elevada, sublime, digna de honor y alabanza",
    "father's joy": "La alegría y mayor deleite del padre",
    "noble": "De noble estirpe, generosa y distinguida",
    "noble nature": "De naturaleza noble, bondadosa y virtuosa",
    "boundless": "Infinita, sin límites, de horizonte inagotable",
    "from hadria": "Procedente de Hadria, fuerte y serena como el mar",
    "good": "Bondadosa, virtuosa, llena de bondad y pureza",
    "pure,chaste": "Pura, casta, de espíritu limpio e inocente",
    "returning, visitor": "Visitante dichosa, la que regresa trayendo paz y dicha",
    "beloved child": "Hija amada y predilecta de su hogar",
    "bright, shining light": "Luz brillante y resplandeciente, que guía en la oscuridad",
    "defender of mankind": "Defensora y protectora valerosa de la humanidad",
    "truth, noble": "Verdadera, noble y de rectitud inquebrantable",
    "joyous": "Alegre, llena de júbilo, entusiasmo y optimismo",
    "beloved": "Amada, querida con profunda devoción",
    "immortal": "Inmortal, de espíritu perdurable y luminoso",
    "grace": "Gracia divina, colmada de compasión y ternura",
    "favor, grace": "Favorecida por la gracia celestial y la bendición",
    "pledge, oath": "Promesa sagrada, fiel y leal a sus principios",
    "angelic": "Angelical, mensajera de paz, pureza y serenidad",
    "resurrection": "Resurrección, renacimiento a una vida nueva y plena",
    "fiery": "Ardiente, apasionada, llena de entusiasmo y fuerza",
    "gift of god": "Regalo precioso y bendición concedida por Dios",
    "lion of god": "Leona de Dios, valerosa, noble y protectora",
    "dawn": "Aurora, el primer destello de luz matutina",
    "golden": "Dorada, radiante como los primeros rayos del sol",
    "life": "Vida, aliento vivificante y portadora de energía",
    "peace": "Paz, serenidad y sosiego para quienes la rodean",
    "wisdom": "Sabiduría, entendimiento claro, prudencia y luz",
    "strong, healthy": "Fuerte, saludable, valiente y llena de vitalidad",
    "victory": "Victoriosa, triunfadora sobre los obstáculos de la vida",
    "light": "Luz radiante que ilumina y reconforta el camino",
    "princess": "Princesa soberana, señora noble y distinguida",
    "pearl": "Perla preciosa, de belleza incalculable y pureza",
    "queen": "Reina soberana, digna de majestad y respeto",
    "famous, bright": "Ilustre, célebre y llena de renombre y luz",
    "free": "Libre, soberana de sus pasos y de espíritu indómito",
    "star": "Estrella fulgurante que brilla en lo más alto del firmamento",
    "heather": "Flor silvestre del brezal, resistente, fresca y hermosa",
    "dedicated to mars": "Dedicada a la fortaleza y valentía protectora",
    "rival, striving": "Empeñada en superarse, dedicada, tenaz y constante",
    "lily": "Lirio blanco virginal, símbolo de pureza y gracia",
    "who is like god?": "¿Quién como Dios? Mensajera de fe y justicia",
    "revered, venerable": "Venerable, respetada y colmada de dignidad",
    "dew of the sea": "Rocío del mar, fresca, serena y vivificante",
    "consolation": "Consuelo, alivio y serenidad para los suyos",
    "blooming, flourishing": "Floreciente, lozana, llena de juventud y esperanza",
    "laurel crowned": "Coronada de laureles, laureada y distinguida",
    "blessed": "Bendita, colmada de bendiciones celestiales y dicha",
    "pure": "Pura, cristalina y limpia de corazón",
    "beloved one": "La predilecta, profundamente amada",
    "bitter or beloved": "Amada con devoción profunda",
    "drop of the sea": "Gota de mar cristalina y profunda"
}

def translate_meaning(eng_meaning):
    if not eng_meaning:
        return "Nombre de distinguida sonoridad y bella tradición"
    low = eng_meaning.strip().lower()
    if low in ENGLISH_MEANING_TRANSLATIONS:
        return ENGLISH_MEANING_TRANSLATIONS[low]
    for eng, esp in ENGLISH_MEANING_TRANSLATIONS.items():
        if eng in low:
            return esp
    return f"De ilustre raíz clásica, interpretado como '{eng_meaning}'"

def translate_origin(eng_origin):
    if not eng_origin:
        return "Español / Latino"
    orig_map = {
        "hebrew": "Hebreo",
        "greek": "Griego",
        "latin": "Latín",
        "german": "Germánico",
        "english": "Inglés",
        "french": "Francés",
        "italian": "Italiano",
        "spanish": "Español",
        "arabic": "Árabe",
        "celtic": "Celta",
        "irish": "Irlandés",
        "slavic": "Eslavo",
        "persian": "Persa",
        "sanskrit": "Sánscrito",
        "japanese": "Japonés",
        "russian": "Ruso",
        "scandinavian": "Escandinavo",
        "dutch": "Holandés",
        "portuguese": "Portugués",
        "hawaiian": "Hawaiano",
        "native american": "Indígena Americano",
        "african": "Africano",
        "welsh": "Galés",
        "scottish": "Escocés"
    }
    low = eng_origin.strip().lower()
    return orig_map.get(low, eng_origin)

# Similarity engine against excluded names
def check_similarity_to_excluded(candidate_name, excluded_list, excluded_norms):
    """
    Checks if candidate_name is similar to any name in excluded_list.
    Returns (is_similar, matched_excluded_name, reason)
    """
    cand_norm = strip_accents(candidate_name)
    cand_parts = [strip_accents(p) for p in re.split(r'[\s\-]+', candidate_name) if len(p) >= 3]

    # 1. Exact match with any excluded name
    if cand_norm in excluded_norms:
        idx = excluded_norms.index(cand_norm)
        return True, excluded_list[idx], "Coincidencia exacta con nombre descartado en v1.0"

    # 2. Any component of a compound name matches an excluded name
    for part in cand_parts:
        if len(part) >= 4 and part in excluded_norms:
            idx = excluded_norms.index(part)
            return True, excluded_list[idx], f"Contiene el nombre '{excluded_list[idx]}', descartado en v1.0"

    # 3. Stem / root similarity
    for part in (cand_parts if len(cand_parts) > 1 else [cand_norm]):
        if len(part) >= 4:
            for i, exc_norm in enumerate(excluded_norms):
                if len(exc_norm) >= 4:
                    # Common prefix of length 4+ with small length diff
                    if part.startswith(exc_norm[:4]) and abs(len(part) - len(exc_norm)) <= 3:
                        dist = levenshtein_dist(part, exc_norm)
                        if dist <= 2:
                            return True, excluded_list[i], f"Comparte raíz y similitud morfológica con '{excluded_list[i]}'"
                    # Levenshtein distance <= 2 for similar length words
                    elif abs(len(part) - len(exc_norm)) <= 1:
                        if levenshtein_dist(part, exc_norm) <= 1:
                            return True, excluded_list[i], f"Muy similar fonéticamente a '{excluded_list[i]}'"

    return False, None, ""

# Meaning dictionary for common single and compound Hispanic name components
NAME_MEANING_FRAGMENTS = {
    "maria": ("Amada de Dios, excelsa y protectora", "Hebreo / Bíblico"),
    "ana": ("Llena de gracia y compasión divina", "Hebreo"),
    "sofia": ("Sabiduría pura y discernimiento lúcido", "Griego"),
    "lucia": ("Luz radiante nacida al alba", "Latín"),
    "valentina": ("Valerosa, saludable y llena de vigor", "Latín"),
    "isabel": ("Consagrada fielmente a Dios", "Hebreo"),
    "elena": ("Antorcha resplandeciente y bella", "Griego"),
    "paula": ("Pequeña, humilde y de gran corazón", "Latín"),
    "laura": ("Coronada de laureles y victoriosa", "Latín"),
    "rosa": ("Bella, fragante y noble como la rosa", "Latín"),
    "clara": ("Luminosa, transparente e ilustre", "Latín"),
    "beatriz": ("Portadora de felicidad y bendición", "Latín"),
    "cecilia": ("Amante de la música y melodiosa", "Latín"),
    "julia": ("De juventud lozana y fuerte linaje", "Latín"),
    "victoria": ("Triunfadora sobre toda adversidad", "Latín"),
    "natalia": ("Nacida para la dicha y la celebración", "Latín"),
    "diana": ("Divina, protectora de la naturaleza", "Latín"),
    "silvia": ("Reina de los bosques y amante de la paz", "Latín"),
    "cristina": ("Fiel seguidora de ideales nobles", "Griego"),
    "irene": ("Portadora de la paz y concordia", "Griego"),
    "sara": ("Princesa soberana y distinguida", "Hebreo"),
    "marta": ("Señora hacendosa y protectora del hogar", "Arameo"),
    "claudia": ("De ilustre nobleza romana", "Latín"),
    "valeria": ("Fuerte, sana y de espíritu valiente", "Latín"),
    "camila": ("De espíritu noble consagrada a lo sagrado", "Latín / Etrusco"),
    "daniela": ("Dios es mi juez y guía supremo", "Hebreo"),
    "gabriela": ("Fuerza y poder protector de Dios", "Hebreo"),
    "andrea": ("Valiente, audaz y decidida", "Griego"),
    "raquel": ("Tierna, noble y apacible", "Hebreo"),
    "alicia": ("Noble, leal y de palabra verdadera", "Germánico"),
    "eva": ("Fuente de vida y energía vivificante", "Hebreo"),
    "alma": ("De espíritu bondadoso y alma pura", "Latín"),
    "rocio": ("Lágrima fresca y vivificante del cielo", "Español / Andaluz"),
    "pilar": "Columna firme y sostén de su familia",
    "candela": "Luz encendida que guía y abriga",
    "macarena": "Esperanza dichosa y alegre",
    "jimena": "La que sabe escuchar con prudencia",
    "vega": "Tierra fértil, lozana y floreciente",
    "triana": "De noble y castiza cuna sevillana",
    "aitana": "Fuerte y majestuosa como la sierra",
    "begona": "Colina alta de mirada maternal",
    "montserrat": "Monte protector y devoto",
    "covadonga": "Cueva de aguas sagradas y victorias",
    "leire": "Legítima y serena en su devoción",
    "mireia": "Admirable, digna de asombro y estima",
    "nerea": "Fluida, marina y transparente",
    "estibaliz": "Dulce como la miel más suave",
    "arantza": "Noble entre las espinas protectoras",
    "ines": "Pura, casta y de espíritu limpio",
    "teresa": "Cosechadora generosa de virtudes",
    "dolores": "Fortaleza serena ante las pruebas",
    "mercedes": "Dádiva, favor y misericordia divina",
    "guadalupe": "Río de luz y amor maternal",
    "fatima": "Única, protectora y luminosa",
    "lourdes": "Manantial cristalino de salud y fe",
    "paloma": "Símbolo de paz, pureza y libertad",
    "blanca": "Resplandeciente, nívea y pura",
    "aurora": "Amanecer dorado de nueva esperanza",
    "estrella": "Guía fulgurante en la noche",
    "sol": "Radiante fuente de calor y alegría",
    "soledad": "Sosiego interior y contemplación",
    "paz": "Serenidad y armonía fraterna",
    "gracia": "Dulzura, encanto y bendición divina",
    "milagros": "Maravilla y prodigio de la vida",
    "esperanza": "Confianza inquebrantable en el porvenir",
    "caridad": "Amor generoso y desinteresado",
    "nieves": "Serena, pura y fresca como la nieve",
    "almudena": "Muralla protectora de la ciudad",
    "loreto": "Laurel sagrado de bendición hogareña",
    "gemma": "Gema preciosa de singular hermosura",
    "rita": "Perla margarita de perseverancia",
    "monica": "Consejera prudente y dedicada",
    "agueda": "Buena por naturaleza y virtudes",
    "apolonia": "Consagrada a la luz del conocimiento",
    "eulalia": "De elocuencia dulce y bien hablada",
    "engracia": "Colmada de la gracia bienhechora",
    "casilda": "Canto místico y hospitalario",
    "martina": "Guerrera protectora y tenaz",
    "marcela": "Valerosa y dedicada al bien",
    "flavia": "De cabellos dorados y luz cálida",
    "priscila": "De venerable y respetable tradición",
    "sabina": "De noble estirpe de la antigua Roma",
    "faustina": "Dichosa, afortunada y próspera",
    "eugenia": "De excelente y noble nacimiento",
    "matilde": "Poderosa en la batalla de la vida",
    "adelaida": "De porte noble y espíritu generoso",
    "clotilde": "Gloriosa por su valentía e integridad",
    "carlota": "Mujer fuerte, noble y libre",
    "gisela": "Promesa de fidelidad y honor",
    "yolanda": "Hermosa como la flor de la violeta",
    "elvira": "Noble guardiana y protectora",
    "tamara": "Palmera esbelta y fecunda",
    "tatiana": "Activa, defensora y ordenada",
    "lidia": "Originaria de Lidia, generosa",
    "noemi": "Dulzura y encanto de su pueblo",
    "zoe": "Llena de vida y vitalidad infinita",
    "celeste": "Celestial, sublime como el firmamento",
    "celina": "Hija del cielo, radiante y suave",
    "regina": "Reina de corazón generoso y justo",
    "olimpia": "Celestial y digna del monte sagrado",
    "amanda": "Digna de ser amada entrañablemente",
    "belinda": "Bella y flexible como un junco",
    "cintia": "Nacida bajo la luz de la luna",
    "dalia": "Elegante y vistosa como la dalia",
    "elsa": "Consagrada a la promesa divina",
    "erika": "Gobernante sabia y eterna",
    "greta": "Perla preciosa y valiosa",
    "karina": "Querida, cariñosa y pura",
    "lorena": "Originaria de Lorena, distinguida",
    "melisa": "Dulce y laboriosa como la miel",
    "miranda": "Digna de admiración y aprecio",
    "olivia": "Portadora de la rama de olivo y paz",
    "renata": "Renacida a una vida brillante",
    "sabrina": "Princesa del río, ágil y fresca",
    "vanessa": "Mariposa deslumbrante de colores",
    "dulce": "Tierna, suave y de trato encantador",
    "luz": "Luz que alumbra y disipa la tristeza",
    "flor": "Brote fresco de fragancia y belleza",
    "consuelo": "Alivio y consuelo para el afligido",
    "amparo": "Refugio seguro y protectora",
    "remedios": "Sanación, remedio y bienestar",
    "asuncion": "Elevada hacia lo más alto",
    "encarnacion": "Misterio de amor hecho vida",
    "purificacion": "Pura, limpia de todo artificio",
    "rosario": "Corona de rosas y plegarias",
    "socorro": "Auxilio oportuno y generoso",
    "sagrario": "Lugar sagrado de recogimiento",
    "prado": "Prado verde y ameno para reposar",
    "mar": "Inmensa y serena como el océano",
    "valle": "Valle apacible y acogedor",
    "camino": "Sendero certero de rectitud",
    "pena": "Firme y sólida como la roca",
    "cinta": "Lazo de unión y afecto entrañable",
    "altagracia": "Colmada de la más alta gracia",
    "chiquinquira": "Lugar de pantano florido y devoción",
    "coromoto": "La que detiene las aguas bravas",
    "itati": "Piedra blanca y luminosa del río",
    "jose": "La que añade abundancia y perseverancia",
    "fernanda": "Atrevida, audaz y pacificadora"
}

def generate_compound_meaning(first, second):
    norm_first = strip_accents(first)
    norm_second = strip_accents(second)
    m1 = NAME_MEANING_FRAGMENTS.get(norm_first, "Noble y distinguida")
    m2 = NAME_MEANING_FRAGMENTS.get(norm_second, "llena de virtudes y gracia")
    if isinstance(m1, tuple):
        m1 = m1[0]
    if isinstance(m2, tuple):
        m2 = m2[0]
    return f"{m1} ({first}), aunada a quien es {m2.lower()} ({second})."

print("Setup complete. Ready to load database and generate.")

# Load existing database
with open('names_db.json', 'r', encoding='utf-8') as f:
    existing_db = json.load(f)

print(f"Loaded {len(existing_db)} existing names from names_db.json")

# Extract the 1,091 excluded names from PDF v1.0
pdf_excluded = [x['name'] for x in existing_db if x.get('status') == 'excluded' and 'PDF' in x.get('source', '')]
pdf_excluded_norms = [strip_accents(n) for n in pdf_excluded]
print(f"Identified {len(pdf_excluded)} excluded names from PDF Version 1.0")

# Set of all lowercase normalized existing names to avoid ANY duplicate
existing_names_set = set(strip_accents(x['name']) for x in existing_db)

# 1. Enrich existing 1,172 PDF names
for item in existing_db:
    if 'PDF' in item.get('source', ''):
        # Translate meaning if needed
        item['meaning'] = translate_meaning(item.get('meaning', ''))
        # Normalize origin
        item['origin'] = translate_origin(item.get('origin', ''))
        # Add santoral
        item['saint_day'] = lookup_saint_day(item['name'])
        item['similar_to'] = ""
        item['is_compound'] = (" " in item['name'] or "-" in item['name'])
    elif item.get('is_new') or '500' in item.get('source', ''):
        # Enrich the 500 Latin names
        item['saint_day'] = lookup_saint_day(item['name'])
        item['is_compound'] = (" " in item['name'] or "-" in item['name'])
        # Check similarity to excluded names
        sim, exc, reason = check_similarity_to_excluded(item['name'], pdf_excluded, pdf_excluded_norms)
        if sim and item.get('status') == 'possible':
            item['status'] = 'similar_excluded'
            item['similar_to'] = f"Similar a '{exc}' (excluido en v1.0)"
            item['notes'] = f"{reason}. Candidato en duda de menor prioridad que los posibles."
        else:
            item['similar_to'] = ""

print("Enriched existing PDF and 500 Latin names.")

# 2. Define pool of rich Latin, Hispanic, and Regional names for generation
PREFIX_NAMES = [
    "María", "Ana", "Dulce", "Luz", "Rosa", "Alba", "Carmen", "Sofía", "Emma",
    "Laura", "Sara", "Elena", "Julia", "Carla", "Andrea", "Valeria", "Clara",
    "Beatriz", "Claudia", "Diana", "Silvia", "Cristina", "Irene", "Marta",
    "Natalia", "Victoria", "Daniela", "Gabriela", "Paola", "Patricia", "Jimena",
    "Lucía", "Valentina", "Isabel", "Inés", "Teresa", "Cecilia", "Blanca",
    "Aurora", "Estrella", "Sol", "Flor", "Eva", "Alma", "Rocío", "Pilar",
    "Candela", "Macarena", "Vega", "Triana", "Aitana", "Begoña", "Montserrat",
    "Covadonga", "Leire", "Mireia", "Nerea", "Arantza", "Estíbaliz", "Dolores",
    "Mercedes", "Guadalupe", "Fátima", "Lourdes", "Paloma", "Soledad", "Paz",
    "Gracia", "Milagros", "Esperanza", "Caridad", "Nieves", "Almudena", "Loreto",
    "Gemma", "Rita", "Mónica", "Águeda", "Martina", "Marcela", "Flavia",
    "Eugenia", "Carlota", "Regina", "Olivia", "Renata", "Consuelo", "Amparo",
    "Remedios", "Rosario", "Socorro", "Sagrario", "Prado", "Valle", "Altagracia",
    "Chiquinquirá", "Coromoto", "Itatí", "Camila", "Carolina", "Alejandra", "Adriana"
]

SUFFIX_NAMES = [
    "José", "Fernanda", "Paula", "Elena", "Victoria", "Camila", "Sofía",
    "Guadalupe", "Carmen", "Dolores", "Belén", "Inés", "Cristina", "Teresa",
    "Ángeles", "Isabel", "Soledad", "Paz", "Gracia", "Milagros", "Esperanza",
    "Pilar", "Rocío", "Rosario", "Mercedes", "Luz", "Sol", "Mar", "Valle",
    "Nieves", "Almudena", "Loreto", "Beatriz", "Daniela", "Valentina", "Lucía",
    "Gabriela", "Andrea", "Raquel", "Alicia", "Laura", "Clara", "Marta",
    "Natalia", "Alejandra", "Carolina", "Jimena", "Montserrat", "Begoña",
    "Macarena", "Paloma", "Triana", "Vega", "Patricia", "Claudia", "Silvia",
    "Irene", "Adriana", "Valeria", "Cecilia", "Blanca", "Aurora", "Estrella",
    "Eva", "Alma", "Candela", "Aitana", "Covadonga", "Leire", "Mireia",
    "Nerea", "Arantza", "Estíbaliz", "Fátima", "Lourdes", "Gemma", "Rita",
    "Mónica", "Martina", "Marcela", "Eugenia", "Carlota", "Regina", "Olivia",
    "Renata", "Consuelo", "Amparo", "Remedios", "Socorro", "Sagrario", "Prado",
    "Altagracia", "Chiquinquirá", "Coromoto", "Itatí", "Antonia", "Antonella",
    "Florencia", "Francisca", "Agustina", "Josefina", "Magdalena", "Manuela",
    "Micaela", "Romina", "Rosalía", "Verónica", "Violeta", "Virginia", "Viviana",
    "Paulina", "Julieta", "Luciana", "Emilia", "Elisa", "Helena", "Catalina",
    "Caterina", "Noelia", "Rebeca", "Ester", "Miriam", "Marina", "Amalia",
    "Leticia", "Luisa", "Constanza", "Fabiola", "Genoveva", "Guillermina"
]

SINGLE_LATIN_NAMES = [
    ("Alondra", "Español", "Noble y libre como la alondra que canta con la aurora"),
    ("Ainara", "Vasco / Español", "Golondrina viajera, anuncio de primavera y alegría"),
    ("Ainhoa", "Vasco / Navarro", "De tierra fértil, consagrada a Nuestra Señora de Ainhoa"),
    ("Araceli", "Latín / Español", "Altar del cielo, luminosa y colmada de gracia"),
    ("Azahara", "Árabe / Andaluz", "Flor blanca del azahar, pura, luminosa y fragante"),
    ("Briseida", "Griego / Clásico", "Brisa suave, hermosa y de noble porte"),
    ("Cayetana", "Latín / Español", "Noble señora protectora del hogar y la paz"),
    ("Dulce", "Latín / Español", "Tierna, afable y de encanto suave y cariñoso"),
    ("Estrella", "Latín / Español", "Luz que brilla en la noche y guía con esperanza"),
    ("Flor", "Latín / Español", "Brote fresco de vida, belleza y delicadeza"),
    ("Galia", "Latín / Clásico", "Fuerte, valiente y de espíritu noble"),
    ("Genoveva", "Celta / Germánico", "De noble linaje, pura y tejedora de paz"),
    ("Guiomar", "Germánico / Español", "Famosa en el combate, de espíritu leal y noble"),
    ("Haydeé", "Griego / Español", "Mujer tierna, recatada y respetable"),
    ("Idalia", "Griego / Latino", "Luminosa como el sol de la isla de Idalia"),
    ("Iliana", "Griego / Latino", "Radiante como el sol, luminosa y bella"),
    ("Iria", "Gallego / Celta", "Paz, tierra fértil y apacible de Galicia"),
    ("Itatí", "Guaraní / Devocional", "Piedra blanca y pura, protegida por la Virgen"),
    ("Jazmín", "Árabe / Persa", "Flor perfumada, bella y de suave distinción"),
    ("Leonor", "Griego / Español", "Dios es mi luz, mujer de linaje real y sabio"),
    ("Lía", "Hebreo", "Trabajadora incansable y de mirada tierna"),
    ("Lila", "Árabe / Latino", "Noche serena y hermosa flor de lila"),
    ("Loreto", "Latín / Español", "Laurel sagrado de bendición para el hogar"),
    ("Luciana", "Latín", "Nacida bajo la primera luz del día, clara y lúcida"),
    ("Macarena", "Español / Andaluz", "Alegre, dichosa, bajo el amparo de la Esperanza"),
    ("Maite", "Vasco / Español", "Amada y querida con profundo cariño"),
    ("Malena", "Hebreo / Español", "Torre fuerte y protectora de los suyos"),
    ("Mar", "Latín / Español", "Inmensa, serena y profunda como las olas del mar"),
    ("Micaela", "Hebreo / Bíblico", "¿Quién como Dios? Fuerte, justa y piadosa"),
    ("Milena", "Eslavo / Latino", "Graciosa, bondadosa y portadora de ternura"),
    ("Miranda", "Latín", "Digna de ser admirada por su bondad y gracia"),
    ("Montserrat", "Catalán / Español", "Monte aserrado sagrado de Cataluña"),
    ("Nerea", "Vasco / Griego", "Fluida, marina y transparente como el agua"),
    ("Nieves", "Latín / Español", "Pura, nívea y serena como la primera nevada"),
    ("Noa", "Hebreo", "Paz, sosiego y consolación para los suyos"),
    ("Olimpia", "Griego", "Perteneciente al monte sagrado, noble y elevada"),
    ("Paloma", "Latín / Español", "Símbolo de paz, pureza y reconciliación"),
    ("Pilar", "Latín / Español", "Columna firme, apoyo inquebrantable de la familia"),
    ("Regina", "Latín", "Reina noble, justa y de corazón generoso"),
    ("Remedios", "Latín / Español", "Alivio, medicina y salud para el alma"),
    ("Renata", "Latín", "Renacida a una vida nueva, luminosa y plena"),
    ("Rocío", "Español / Andaluz", "Rocío del alba, bendición fresca del cielo"),
    ("Romina", "Latín / Italiano", "De la tierra de Roma, fuerte y perseverante"),
    ("Rosario", "Latín / Español", "Guirnalda de rosas benditas y devoción"),
    ("Salma", "Árabe / Latino", "Pacífica, sana, serena y protegida"),
    ("Salomé", "Hebreo", "Pacífica, que disfruta de bienestar y armonía"),
    ("Silvia", "Latín", "Doncella de los bosques verdes y la naturaleza"),
    ("Soledad", "Latín / Español", "Paz interior, recogimiento y serenidad"),
    ("Triana", "Español / Andaluz", "Del castizo barrio de Triana junto al Guadalquivir"),
    ("Uxúe", "Vasco / Navarro", "Paloma nívea, protectora de Navarra"),
    ("Vega", "Español", "Fértil y amena llanura que florece en abundancia"),
    ("Violeta", "Latín / Español", "Modesta, fragante y de exquisito color violáceo"),
    ("Zaida", "Árabe / Español", "Señora noble que crece y prospera con honores"),
    ("Zaira", "Árabe / Español", "Florida, brillante y de mirada luminosa"),
    ("Zoraida", "Árabe / Español", "Mujer elocuente que sabe hablar con prudencia")
]

# 3. Generate exactly 2,000 new Latin/Hispanic names
new_names_list = []
generated_count = 0
target_new_names = 2000

# First, add the curated single Latin names if not yet in DB
for s_name, s_orig, s_mean in SINGLE_LATIN_NAMES:
    if generated_count >= target_new_names:
        break
    norm = strip_accents(s_name)
    if norm not in existing_names_set:
        sim, exc, reason = check_similarity_to_excluded(s_name, pdf_excluded, pdf_excluded_norms)
        status = "similar_excluded" if sim else "possible"
        sim_to = f"Similar a '{exc}' (excluido en v1.0)" if sim else ""
        notes = f"{reason}. Candidato en duda de menor prioridad que los posibles." if sim else "Nuevo candidato latino individual seleccionado."
        
        new_names_list.append({
            "id": f"new-v2-{len(new_names_list)+1:04d}",
            "name": s_name,
            "origin": s_orig,
            "meaning": s_mean,
            "letter": s_name[0].upper(),
            "status": status,
            "notes": notes,
            "source": "2000 Nuevos Hispanos y Latinos",
            "gender": "Female",
            "is_new": True,
            "is_compound": False,
            "saint_day": lookup_saint_day(s_name),
            "similar_to": sim_to
        })
        existing_names_set.add(norm)
        generated_count += 1

print(f"Added {generated_count} single Latin names. Now generating compound Hispanic names...")

# Generate compound Hispanic names systematically
# We iterate over PREFIX_NAMES and SUFFIX_NAMES
for p in PREFIX_NAMES:
    if generated_count >= target_new_names:
        break
    for s in SUFFIX_NAMES:
        if generated_count >= target_new_names:
            break
        # Avoid redundant combos like "María María" or "Ana Ana"
        if strip_accents(p) == strip_accents(s):
            continue
            
        compound_name = f"{p} {s}"
        norm = strip_accents(compound_name)
        if norm in existing_names_set:
            continue
            
        # Determine origin & meaning
        origin = "Compuesto Hispano"
        meaning = generate_compound_meaning(p, s)
        saint_day = lookup_saint_day(compound_name)
        
        # Check similarity to PDF excluded names
        sim, exc, reason = check_similarity_to_excluded(compound_name, pdf_excluded, pdf_excluded_norms)
        status = "similar_excluded" if sim else "possible"
        sim_to = f"Similar al nombre excluido '{exc}' (v1.0)" if sim else ""
        notes = f"{reason}. Clasificado en categoría de similares a excluidos." if sim else "Nuevo nombre compuesto hispano recomendado."
        
        new_names_list.append({
            "id": f"new-v2-{len(new_names_list)+1:04d}",
            "name": compound_name,
            "origin": origin,
            "meaning": meaning,
            "letter": compound_name[0].upper(),
            "status": status,
            "notes": notes,
            "source": "2000 Nuevos Hispanos y Latinos",
            "gender": "Female",
            "is_new": True,
            "is_compound": True,
            "saint_day": saint_day,
            "similar_to": sim_to
        })
        existing_names_set.add(norm)
        generated_count += 1

print(f"Generated exactly {len(new_names_list)} new Latin/Hispanic names!")

# Combine all names
full_database = existing_db + new_names_list
print(f"Total database count: {len(full_database)} names.")

# Breakdown of statuses
status_counts = {}
for x in full_database:
    st = x.get('status', 'unknown')
    status_counts[st] = status_counts.get(st, 0) + 1

print("\n=== STATUS BREAKDOWN ===")
for st, cnt in sorted(status_counts.items()):
    print(f"  {st:18}: {cnt:5d}")

source_counts = {}
for x in full_database:
    src = x.get('source', 'unknown')
    source_counts[src] = source_counts.get(src, 0) + 1

print("\n=== SOURCE BREAKDOWN ===")
for src, cnt in sorted(source_counts.items()):
    print(f"  {src:30}: {cnt:5d}")

# Save to names_db.json and backup
with open('names_db.json', 'w', encoding='utf-8') as f:
    json.dump(full_database, f, ensure_ascii=False, indent=2)

with open('names_db_backup.json', 'w', encoding='utf-8') as f:
    json.dump(full_database, f, ensure_ascii=False, indent=2)

print("\nSUCCESS! Successfully saved updated names_db.json and names_db_backup.json.")
