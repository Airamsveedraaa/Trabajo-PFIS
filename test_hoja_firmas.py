import unittest
from hoja_firmas import leer_csv, ordenar_alumnos, agrupar_en_grupos
import tempfile
import os


class TestLeerCSV(unittest.TestCase):

    def setUp(self):
        """Crea un CSV temporal para los tests."""
        self.csv_temporal = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        )
        self.csv_temporal.write("Nombre; Apellido(s)\n")
        self.csv_temporal.write("Pikachu; Aurelius\n")
        self.csv_temporal.write("Bulbasaur; Claudius\n")
        self.csv_temporal.write("Charmander; Julius\n")
        self.csv_temporal.close()

    def tearDown(self):
        os.unlink(self.csv_temporal.name)

    def test_leer_csv_devuelve_lista(self):
        resultado = leer_csv(self.csv_temporal.name)
        self.assertIsInstance(resultado, list)

    def test_leer_csv_cantidad_correcta(self):
        resultado = leer_csv(self.csv_temporal.name)
        self.assertEqual(len(resultado), 3)

    def test_leer_csv_estructura_dict(self):
        resultado = leer_csv(self.csv_temporal.name)
        self.assertIn('nombre', resultado[0])
        self.assertIn('apellidos', resultado[0])

    def test_leer_csv_valores_correctos(self):
        resultado = leer_csv(self.csv_temporal.name)
        nombres = [a['nombre'] for a in resultado]
        self.assertIn('Pikachu', nombres)
        self.assertIn('Bulbasaur', nombres)

    def test_leer_csv_sin_espacios_extra(self):
        resultado = leer_csv(self.csv_temporal.name)
        for alumno in resultado:
            self.assertEqual(alumno['nombre'], alumno['nombre'].strip())
            self.assertEqual(alumno['apellidos'], alumno['apellidos'].strip())


class TestOrdenarAlumnos(unittest.TestCase):

    def setUp(self):
        self.alumnos = [
            {'nombre': 'Zapdos', 'apellidos': 'Z'},
            {'nombre': 'Articuno', 'apellidos': 'A'},
            {'nombre': 'Moltres', 'apellidos': 'M'},
        ]

    def test_orden_alfabetico(self):
        resultado = ordenar_alumnos(self.alumnos)
        nombres = [a['nombre'] for a in resultado]
        self.assertEqual(nombres, sorted(nombres, key=str.lower))

    def test_primer_elemento_correcto(self):
        resultado = ordenar_alumnos(self.alumnos)
        self.assertEqual(resultado[0]['nombre'], 'Articuno')

    def test_ultimo_elemento_correcto(self):
        resultado = ordenar_alumnos(self.alumnos)
        self.assertEqual(resultado[-1]['nombre'], 'Zapdos')

    def test_no_modifica_lista_original(self):
        original = [a['nombre'] for a in self.alumnos]
        ordenar_alumnos(self.alumnos)
        actual = [a['nombre'] for a in self.alumnos]
        self.assertEqual(original, actual)

    def test_lista_vacia(self):
        self.assertEqual(ordenar_alumnos([]), [])

    def test_un_elemento(self):
        uno = [{'nombre': 'Pikachu', 'apellidos': 'A'}]
        self.assertEqual(ordenar_alumnos(uno), uno)


class TestAgruparEnGrupos(unittest.TestCase):

    def setUp(self):
        self.alumnos = [{'nombre': f'Pokemon{i}', 'apellidos': 'X'} for i in range(20)]

    def test_grupos_de_8(self):
        grupos = agrupar_en_grupos(self.alumnos, 8)
        for grupo in grupos[:-1]:  # todos menos el último
            self.assertEqual(len(grupo), 8)

    def test_cantidad_grupos_correcta(self):
        grupos = agrupar_en_grupos(self.alumnos, 8)
        self.assertEqual(len(grupos), 3)  # 20 -> 8, 8, 4

    def test_ultimo_grupo_resto(self):
        grupos = agrupar_en_grupos(self.alumnos, 8)
        self.assertEqual(len(grupos[-1]), 4)  # 20 % 8 = 4

    def test_lista_vacia(self):
        self.assertEqual(agrupar_en_grupos([], 8), [])

    def test_exactamente_un_grupo(self):
        seis = [{'nombre': f'P{i}', 'apellidos': 'X'} for i in range(6)]
        grupos = agrupar_en_grupos(seis, 8)
        self.assertEqual(len(grupos), 1)
        self.assertEqual(len(grupos[0]), 6)

    def test_todos_los_alumnos_presentes(self):
        grupos = agrupar_en_grupos(self.alumnos, 8)
        total = sum(len(g) for g in grupos)
        self.assertEqual(total, len(self.alumnos))

    def test_tamanyo_personalizado(self):
        grupos = agrupar_en_grupos(self.alumnos, 5)
        for grupo in grupos[:-1]:
            self.assertEqual(len(grupo), 5)


if __name__ == '__main__':
    unittest.main()
