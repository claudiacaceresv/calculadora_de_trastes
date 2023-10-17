import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image
import fitz

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de trastes",
    page_icon="image/icon/icon.png",
    layout="wide"
)

# Titulo
st.title("Calculadora de Trastes")

# Elementos interactivos
trastes_usuario = st.text_input("Número de trastes:")
unidad = st.radio("Unidad del Tiro de Cuerda:", ("milímetros", "pulgadas"))

# Tiro de cuerda en función de la unidad elegida
if unidad == "milímetros":
    tiro_de_cuerda_usuario = st.text_input("Tiro de cuerda (mm):")
else:
    tiro_de_cuerda_usuario = st.text_input("Tiro de cuerda (in):")

# Botón para calcular
if st.button("Calcular"):
    try:
        # Verificar que el número de trastes sea un valor válido
        if trastes_usuario.isnumeric():
            trastes = int(trastes_usuario)
            tiro_de_cuerda_usuario = float(tiro_de_cuerda_usuario)

            num = 17.817
            in_a_mm = 25.4
            mm_a_in = 0.0393701

            if unidad == "milímetros":
                tiro_de_cuerda = tiro_de_cuerda_usuario * mm_a_in
            else:
                tiro_de_cuerda = tiro_de_cuerda_usuario

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

            df_in = pd.DataFrame(data, columns=['Traste N°', 'Distancia a la cejuela', 'Tamaño del traste', 'Distancia al puente'])

            if unidad == "milímetros":
                df_mm = df_in.copy()
                df_mm[['Distancia a la cejuela', 'Tamaño del traste', 'Distancia al puente']] *= in_a_mm

            # GENERAR GRÁFICO DE TRASTES PDF
            df_grafico = df_in.copy()

            # Tamaño gráfico
            cantidad_lineas_horizontales = 10
            medida_lineas_horizontales = 5 * mm_a_in

            ancho_gráfico = df_grafico['Distancia a la cejuela'].max() + (15 * mm_a_in)
            alto_gráfico = cantidad_lineas_horizontales * medida_lineas_horizontales

            # Tamaño hoja
            ancho_hoja = ancho_gráfico + 10 * mm_a_in
            alto_hoja = alto_gráfico + 10 * mm_a_in

            # Crear un archivo PDF con el tamaño del gráfico
            pdf_archivo = "grafico.pdf"
            c = canvas.Canvas(pdf_archivo, pagesize=(ancho_hoja * inch, alto_hoja * inch))
            c.setLineWidth(0.5)

            # Coordenadas para el punto de inicio del rectángulo (x, y) en pulgadas
            x = (ancho_hoja - ancho_gráfico) / 2
            y = (alto_hoja - alto_gráfico) / 2

            # Dibujar el rectángulo (dentro de la hoja)
            c.rect(x * inch, y * inch, ancho_gráfico * inch, alto_gráfico * inch)

            # Dibujar las líneas horizontales
            numero_lineas = int(alto_gráfico / medida_lineas_horizontales) + 1
            for i in range(numero_lineas):
                linea_y = y * inch + i * medida_lineas_horizontales * inch
                c.line(x * inch, linea_y, (x + ancho_gráfico) * inch, linea_y)

            # Dibujar la primera línea vertical que inicie los trastes
            # Dibujar la línea vertical desde el borde izquierdo del gráfico hasta la primera línea
            x1 = x + medida_lineas_horizontales
            y1 = y
            x2 = x + medida_lineas_horizontales
            y2 = alto_hoja - medida_lineas_horizontales
            c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)

            # Dibujar los trastes
            for index, row in df_grafico.iterrows():
                x1 = x + row['Distancia a la cejuela']
                y1 = y
                x2 = x1
                y2 = alto_hoja - medida_lineas_horizontales
                c.line(x1 * inch, y1 * inch, x2 * inch, y2 * inch)

            # Agregar título
            titulo = f"Tiro de cuerda: {round(tiro_de_cuerda_usuario, 3)} {unidad} | Cantidad de trastes: {trastes}"
            c.setFont("Helvetica", 10)
            c.drawString(x * inch, y * inch + alto_gráfico * inch + 4, titulo)

            # Agregar un sitio web debajo del gráfico en el borde opuesto
            web = "https://calculadora-de-trastes.streamlit.app/"
            c.setFont("Helvetica", 8)
            web_x = x * inch  # Colocar el sitio web en el borde izquierdo del gráfico
            web_y = y * inch - 10  # Ajusta la posición vertical según tus preferencias
            c.drawString(web_x, web_y, web)  # Coloca el sitio web en la posición especificada

            # Guardar y cerrar el archivo PDF
            c.showPage()
            c.save()

            # Abre el archivo PDF con PyMuPDF
            pdf_document = fitz.open(pdf_archivo)

            # Convierte la página del PDF en una imagen
            page = pdf_document.load_page(0)

                        # Aumenta la resolución (DPI) para obtener una imagen de mayor calidad
            dpi = 300
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))

            # Ruta donde se guardará la imagen
            imagen_pdf_path = "image/graficos.pdf.png"

            # Guarda la imagen en la ubicación fija
            pix.save(imagen_pdf_path, "png")

            # Carga la imagen desde la ubicación fija con Pillow
            imagen_pdf = Image.open(imagen_pdf_path)

            # GENERAR GRÁFICO DE TABLA
            if unidad == "milímetros":
                df_mm.columns = ["Traste N°", "Distancia a la cejuela", "Tamaño del traste", "Distancia al puente"]
            else:
                df_in.columns = ["Traste N°", "Distancia a la cejuela", "Tamaño del traste", "Distancia al puente"]

            # Convertir la cadena de la tabla en una tabla de matplotlib, redondear los números y formatear la columna "Traste" como texto
            if unidad == "milímetros":
                fig_tabla, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')  # Ocultar los ejes
                df_mm_rounded = df_mm.round(3)
                df_mm_rounded["Traste N°"] = df_mm_rounded["Traste N°"].astype(int).astype(str)
                tabla_data = df_mm_rounded.values
                tabla_col_labels = df_mm_rounded.columns
            else:
                fig_tabla, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')  # Ocultar los ejes
                df_in_rounded = df_in.round(3)
                df_in_rounded["Traste N°"] = df_in_rounded["Traste N°"].astype(int).astype(str)
                tabla_data = df_in_rounded.values
                tabla_col_labels = df_in_rounded.columns

            # Ajustar el ancho de las filas para dar más espacio a los datos
            tabla = ax.table(cellText=tabla_data, colLabels=tabla_col_labels, cellLoc='center', loc='center')
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(10)
            tabla.scale(1, 1.5)  # Ajusta el ancho de las filas

            # Guardar la tabla en un archivo PDF separado
            tabla_pdf = "tabla_trastes.pdf"
            with PdfPages(tabla_pdf) as pdf:
                pdf.savefig(fig_tabla)
            st.write('---')

            # DESCARGAR PDF
            # Leer el archivo PDF como datos binarios
            with open(pdf_archivo, "rb") as pdf_file:
                pdf_bytes_grafico = pdf_file.read()

            # Nombre archivo
            plano_nombre_pdf = f"plano_tiro_de_cuerda_{tiro_de_cuerda_usuario}_{unidad}_{trastes}_trastes.pdf"

            # Muestra un enlace para descargar el PDF
            st.markdown(f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes_grafico).decode()}" download="{plano_nombre_pdf}">Descargar Plano -  PDF</a>', unsafe_allow_html=True)

            # Leer el archivo PDF de la tabla como datos binarios
            with open(tabla_pdf, "rb") as tabla_pdf_file:
                pdf_bytes_tabla = tabla_pdf_file.read()

            # Nombre archivo
            tabla_nombre_pdf = f"tabla_tiro_de_cuerda_{tiro_de_cuerda_usuario}_{unidad}_{trastes}_trastes.pdf"

            # Agregar botón para descargar el PDF de la tabla
            st.markdown(f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes_tabla).decode()}" download="{tabla_nombre_pdf}">Descargar Tabla - PDF</a>', unsafe_allow_html=True)

            st.write('---')

            # MOSTRAR LOS GRAFICOS
            # Mostrar la imagen en Streamlit
            st.image(imagen_pdf, use_column_width=True)

            # Mostrar el gráfico de la tabla
            st.pyplot(fig_tabla)

        else:
            st.error("Por favor, ingresa un valor numérico entero válido para la cantidad de trastes")
    except ValueError:
        st.error("Por favor, ingresa un valor válido para el tiro de cuerda en milímetros")

st.write('---')

# Muestra el mensaje con las URLs
# URL de GitHub
github_url = 'https://github.com/claudiacaceresv/calculadora_de_trastes'
st.write(f"El código fuente está disponible en el siguiente repositorio para su uso público en *GitHub*: {github_url}")

st.write('---')

# Cargar la imagen
image = Image.open('image/icon/linkedin.png')

# URL de LinkedIn
linkedin_url = 'https://www.linkedin.com/in/claudiacaceresv'

# Ajustar el tamaño de la imagen
small_image = image.resize((50, 50))

# En Streamlit, simplemente coloca los elementos uno debajo del otro
st.image(small_image, use_column_width=False)
st.write(f'[LinkedIn]({linkedin_url})')

