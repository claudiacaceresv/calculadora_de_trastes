import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
import streamlit as st
import io
import base64
from tabulate import tabulate

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de trastes",
    page_icon="image/icon.png",
    layout="wide"
)

# Titulo
st.title("Calculadora de Trastes")

# Elementos interactivos
trastes_usuario = st.text_input("Numero de trastes:")
tiro_de_cuerda_usuario = st.text_input("Tiro de cuerda (mm):")

# Botón para calcular
if st.button("Calcular"):
    try:
        # Verificar que el número de trastes sea valor válido
        if trastes_usuario.isnumeric():
            trastes = int(trastes_usuario)
            tiro_de_cuerda_usuario = float(tiro_de_cuerda_usuario)

            pulgadas = 25.4
            num = 17.817
            tiro_de_cuerda = tiro_de_cuerda_usuario / pulgadas

            # Cálculo de los datos para el gráfico
            data = []

            distancia_a_la_cejuela = 0

            for traste in range(1, trastes + 1):
                if traste == 1:
                    tamano_del_traste = tiro_de_cuerda / num
                    distancia_a_la_cejuela = tamano_del_traste
                    distancia_al_puente = tiro_de_cuerda - tamano_del_traste
                data.append([traste, distancia_a_la_cejuela, tamano_del_traste, distancia_al_puente])
                tamano_del_traste = distancia_al_puente / num
                distancia_al_puente = distancia_al_puente - tamano_del_traste
                distancia_a_la_cejuela = distancia_a_la_cejuela + tamano_del_traste

            df_in = pd.DataFrame(data, columns=['traste', 'distancia_a_la_cejuela', 'tamano_del_traste', 'distancia_al_puente'])

            # Crear una copia del DataFrame original para mantener los valores en pulgadas
            df_mm = df_in.copy()

            # Multiplicar las columnas relevantes por pulgadas
            df_mm[['distancia_a_la_cejuela', 'tamano_del_traste', 'distancia_al_puente']] *= pulgadas

            # Configuración del gráfico
            ancho_grafico = df_in["distancia_a_la_cejuela"].max() + (15 / pulgadas)
            alto_grafico = 30 / pulgadas

            fig, ax = plt.subplots(figsize=(ancho_grafico, alto_grafico), dpi=300)

            # Variable para almacenar la posición de la cejuela
            posicion_cejuela = 5 / pulgadas

            # Dibuja una línea vertical en la posición de la cejuela
            traste_line = Line2D([posicion_cejuela, posicion_cejuela], [-0.5, 2.0], color="black", lw=1)
            ax.add_line(traste_line)

            # Dibuja el diapasón como un rectángulo blanco
            diapason = Rectangle((0, -0.2), ancho_grafico, alto_grafico, color='white')
            ax.add_patch(diapason)

            # Dibuja los trastes como líneas verticales
            for traste in df_in.itertuples():
                tamano_traste = traste.tamano_del_traste
                posicion_cejuela += tamano_traste

                traste_line = Line2D([posicion_cejuela, posicion_cejuela], [-0.5, 2.0], color='black', lw=1)
                ax.add_line(traste_line)

            # Ajusta el espacio entre las líneas horizontales a 5 mm (0.5 en la escala del gráfico)
            espacio_entre_lineas = 0.5

            # Ajusta el límite superior del eje y para acomodar las líneas horizontales
            ax.set_ylim(0, 1.5 + espacio_entre_lineas)

            # Dibuja las líneas horizontales para representar los trastes
            posicion_linea = espacio_entre_lineas  # Comienza desde la primera línea

            for _ in range(int(2 / espacio_entre_lineas)):
                traste_line = Line2D([0, tiro_de_cuerda], [posicion_linea, posicion_linea], color='black', lw=1)
                ax.add_line(traste_line)
                posicion_linea += espacio_entre_lineas

            # Desactiva las etiquetas en el eje "y"
            ax.set_yticklabels([])
            ax.set_yticks([])

            # Desactiva las etiquetas en el eje "x"
            ax.set_xticklabels([])
            ax.set_xticks([])

            # Ajusta el rango del eje x para que se adapte a la longitud de la cuerda
            ax.set_xlim(0, ancho_grafico)

            # Ajustar los márgenes para dejar espacio para el título
            plt.subplots_adjust(top=0.7, bottom=0.1)

            # Mostrar el título del gráfico
            titulo = f'Tiro de cuerda: {tiro_de_cuerda_usuario} mm | Cantidad de trastes: {trastes}'
            plt.title(titulo, fontsize=10)

            # Guardar el gráfico en un archivo PDF
            pdf_bytes = io.BytesIO()
            with PdfPages(pdf_bytes) as pdf:
                pdf.savefig(fig, bbox_inches="tight")

            # Cambiar el nombre de las columnas
            df_mm.columns = ["Traste N°", "Distancia a la cejuela", "Tamaño del traste", "Distancia al puente"]

            # Crear una figura de Matplotlib
            fig_tabla, ax = plt.subplots()

            # Crear una representación en formato de tabla del DataFrame sin mostrar la columna del índice
            table = tabulate(df_mm, headers='keys', tablefmt='grid', showindex=False)

            # Mostrar la tabla en la figura
            ax.text(0.1, 0.1, table, {'family': 'monospace'}, fontsize=10)

            # Configurar la figura
            ax.axis('off')

            # Guardar el gráfico de la tabla en un archivo PDF
            pdf_bytes_tabla = io.BytesIO()
            with PdfPages(pdf_bytes_tabla) as pdf:
                pdf.savefig(fig_tabla, bbox_inches="tight")

            # Agregar botón para descargar el PDF
            st.markdown(f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes.getvalue()).decode()}" download="grafico_tiro_de_cuerda_{int(tiro_de_cuerda_usuario)}_mm_trastes_{trastes}.pdf">Descargar Gráfico - PDF</a>', unsafe_allow_html=True)

            # Agregar botón para descargar el PDF del gráfico de la tabla
            st.markdown(f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes_tabla.getvalue()).decode()}" download="tabla_tiro_de_cuerda_{int(tiro_de_cuerda_usuario)}_mm_trastes_{trastes}.pdf">Descargar Tabla - PDF</a>', unsafe_allow_html=True)

            # Mostrar el gráfico
            st.pyplot(fig)

            # Mostrar el gráfico de la tabla
            st.pyplot(fig_tabla)

        else:
            st.error("Por favor, ingresa un valor numérico entero válido para la cantidad de trastes")
    except ValueError:
        st.error("Por favor, ingresa un valor válido para el tiro de cuerda en milímetros")
